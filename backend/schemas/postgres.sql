CREATE TABLE subjects (
  uid TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sections (
  uid TEXT PRIMARY KEY,
  subject_uid TEXT NOT NULL REFERENCES subjects(uid) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  order_index INT NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX section_scope_title_unique ON sections(subject_uid, title);

CREATE TABLE topics (
  uid TEXT PRIMARY KEY,
  section_uid TEXT NOT NULL REFERENCES sections(uid) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  accuracy_threshold NUMERIC,
  critical_errors_max INT,
  median_time_threshold_seconds INT
);

CREATE UNIQUE INDEX topic_scope_title_unique ON topics(section_uid, title);

CREATE TABLE skills (
  uid TEXT PRIMARY KEY,
  subject_uid TEXT NOT NULL REFERENCES subjects(uid) ON DELETE CASCADE,
  title TEXT NOT NULL,
  definition TEXT DEFAULT '',
  applicability_types TEXT[] DEFAULT '{}',
  type TEXT,
  status TEXT DEFAULT 'active'
);

CREATE UNIQUE INDEX skill_scope_title_unique ON skills(subject_uid, title);

CREATE TABLE methods (
  uid TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  method_text TEXT DEFAULT '',
  applicability_types TEXT[] DEFAULT '{}'
);

CREATE TABLE examples (
  uid TEXT PRIMARY KEY,
  subject_uid TEXT REFERENCES subjects(uid) ON DELETE CASCADE,
  topic_uid TEXT REFERENCES topics(uid) ON DELETE SET NULL,
  title TEXT NOT NULL,
  statement TEXT DEFAULT '',
  difficulty_level TEXT NOT NULL DEFAULT 'medium'
);

CREATE TABLE errors (
  uid TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  error_text TEXT DEFAULT '',
  triggers TEXT[] DEFAULT '{}'
);

CREATE TABLE topic_skills (
  topic_uid TEXT NOT NULL REFERENCES topics(uid) ON DELETE CASCADE,
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  PRIMARY KEY(topic_uid, skill_uid)
);

CREATE TABLE skill_methods (
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  method_uid TEXT NOT NULL REFERENCES methods(uid) ON DELETE CASCADE,
  weight TEXT NOT NULL DEFAULT 'secondary',
  confidence NUMERIC NOT NULL DEFAULT 0.5,
  is_auto_generated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (skill_uid, method_uid),
  CHECK (confidence >= 0.0 AND confidence <= 1.0),
  CHECK (weight IN ('primary','secondary','auxiliary'))
);

CREATE TABLE example_skills (
  example_uid TEXT NOT NULL REFERENCES examples(uid) ON DELETE CASCADE,
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('target','aux','context')),
  PRIMARY KEY(example_uid, skill_uid)
);

CREATE TABLE error_skills (
  error_uid TEXT NOT NULL REFERENCES errors(uid) ON DELETE CASCADE,
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  PRIMARY KEY(error_uid, skill_uid)
);

CREATE TABLE error_examples (
  error_uid TEXT NOT NULL REFERENCES errors(uid) ON DELETE CASCADE,
  example_uid TEXT NOT NULL REFERENCES examples(uid) ON DELETE CASCADE,
  PRIMARY KEY(error_uid, example_uid)
);

CREATE TABLE topic_prereq (
  topic_uid TEXT NOT NULL REFERENCES topics(uid) ON DELETE CASCADE,
  prereq_uid TEXT NOT NULL REFERENCES topics(uid) ON DELETE CASCADE,
  PRIMARY KEY(topic_uid, prereq_uid)
);

CREATE OR REPLACE FUNCTION check_skill_method_applicability()
RETURNS TRIGGER AS $$
DECLARE s_type TEXT; m_types TEXT[];
BEGIN
  SELECT type INTO s_type FROM skills WHERE uid = NEW.skill_uid;
  SELECT applicability_types INTO m_types FROM methods WHERE uid = NEW.method_uid;
  IF m_types IS NOT NULL AND cardinality(m_types) > 0 AND s_type IS NOT NULL THEN
    IF NOT (s_type = ANY(m_types)) THEN
      RAISE EXCEPTION 'inapplicable method type';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_skill_method_applicability ON skill_methods;
CREATE TRIGGER trg_skill_method_applicability BEFORE INSERT OR UPDATE ON skill_methods
FOR EACH ROW EXECUTE FUNCTION check_skill_method_applicability();

CREATE OR REPLACE FUNCTION check_prereq_dag()
RETURNS TRIGGER AS $$
DECLARE has_cycle BOOLEAN;
BEGIN
  WITH RECURSIVE walk(uid) AS (
    SELECT NEW.prereq_uid
    UNION ALL
    SELECT tp.prereq_uid FROM topic_prereq tp JOIN walk w ON tp.topic_uid = w.uid
  )
  SELECT EXISTS(SELECT 1 FROM walk WHERE uid = NEW.topic_uid) INTO has_cycle;
  IF has_cycle THEN
    RAISE EXCEPTION 'cycle detected in PREREQ';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prereq_dag ON topic_prereq;
CREATE TRIGGER trg_prereq_dag BEFORE INSERT OR UPDATE ON topic_prereq
FOR EACH ROW EXECUTE FUNCTION check_prereq_dag();

CREATE TABLE skill_prerequisites (
  subject_uid TEXT NOT NULL REFERENCES subjects(uid) ON DELETE CASCADE,
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  depends_on_skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE CASCADE,
  CHECK (skill_uid <> depends_on_skill_uid),
  PRIMARY KEY (subject_uid, skill_uid, depends_on_skill_uid)
);

CREATE OR REPLACE FUNCTION check_skill_prereq_same_subject()
RETURNS TRIGGER AS $$
DECLARE s1 TEXT; s2 TEXT;
BEGIN
  SELECT subject_uid INTO s1 FROM skills WHERE uid = NEW.skill_uid;
  SELECT subject_uid INTO s2 FROM skills WHERE uid = NEW.depends_on_skill_uid;
  IF s1 IS NULL OR s2 IS NULL THEN
    RAISE EXCEPTION 'Skill UIDs must exist';
  END IF;
  IF s1 <> NEW.subject_uid OR s2 <> NEW.subject_uid THEN
    RAISE EXCEPTION 'Both skills must belong to subject %', NEW.subject_uid;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_skill_prereq_same_subject ON skill_prerequisites;
CREATE TRIGGER trg_skill_prereq_same_subject
BEFORE INSERT OR UPDATE ON skill_prerequisites
FOR EACH ROW EXECUTE FUNCTION check_skill_prereq_same_subject();

CREATE OR REPLACE FUNCTION check_skill_prerequisite_acyclic()
RETURNS TRIGGER AS $$
DECLARE cycle_found BOOLEAN;
BEGIN
  WITH RECURSIVE reach(n) AS (
    SELECT NEW.depends_on_skill_uid
    UNION
    SELECT sp.depends_on_skill_uid
    FROM skill_prerequisites sp
    JOIN reach r ON sp.skill_uid = r.n
    WHERE sp.subject_uid = NEW.subject_uid
  )
  SELECT EXISTS (
    SELECT 1 FROM reach WHERE n = NEW.skill_uid
  ) INTO cycle_found;

  IF cycle_found THEN
    RAISE EXCEPTION 'Cycle detected in prerequisites for subject %: % -> %', NEW.subject_uid, NEW.skill_uid, NEW.depends_on_skill_uid;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_skill_prereq_acyclic ON skill_prerequisites;
CREATE TRIGGER trg_skill_prereq_acyclic
BEFORE INSERT OR UPDATE ON skill_prerequisites
FOR EACH ROW EXECUTE FUNCTION check_skill_prerequisite_acyclic();

CREATE TABLE attempts (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  example_uid TEXT NOT NULL REFERENCES examples(uid) ON DELETE RESTRICT,
  source TEXT,
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  time_spent_sec INT CHECK (time_spent_sec >= 0),
  accuracy NUMERIC CHECK (accuracy >= 0 AND accuracy <= 1),
  critical_errors_count INT DEFAULT 0 CHECK (critical_errors_count >= 0)
);

CREATE TABLE steps (
  id BIGSERIAL PRIMARY KEY,
  attempt_id BIGINT NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
  step_order INT NOT NULL,
  action TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX steps_attempt_order_unique ON steps(attempt_id, step_order);

CREATE TABLE evaluations (
  id BIGSERIAL PRIMARY KEY,
  attempt_id BIGINT NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
  skill_uid TEXT NOT NULL REFERENCES skills(uid) ON DELETE RESTRICT,
  role TEXT NOT NULL CHECK (role IN ('target','aux','context')),
  accuracy NUMERIC NOT NULL,
  critical BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE error_events (
  id BIGSERIAL PRIMARY KEY,
  attempt_id BIGINT NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
  error_uid TEXT NOT NULL REFERENCES errors(uid) ON DELETE RESTRICT,
  skill_uid TEXT REFERENCES skills(uid) ON DELETE RESTRICT,
  example_uid TEXT REFERENCES examples(uid) ON DELETE RESTRICT,
  critical BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sections_subject_uid ON sections(subject_uid);
CREATE INDEX IF NOT EXISTS idx_topics_section_uid ON topics(section_uid);
CREATE INDEX IF NOT EXISTS idx_skills_subject_uid ON skills(subject_uid);
CREATE INDEX IF NOT EXISTS idx_examples_topic_uid ON examples(topic_uid);
