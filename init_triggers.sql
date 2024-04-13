CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE OR REPLACE FUNCTION generate_uuid()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

ALTER TABLE banners_banner
ALTER COLUMN uuid SET DEFAULT generate_uuid();

CREATE SEQUENCE banners_banner_id_seq AS integer;

ALTER TABLE banners_banner ALTER COLUMN id SET DEFAULT nextval('banners_banner_id_seq');

SELECT setval('banners_banner_id_seq', COALESCE(MAX(id), 0) + 1) FROM banners_banner;

CREATE OR REPLACE FUNCTION set_banner_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id IS NULL THEN
        NEW.id := nextval('banners_banner_id_seq');
    END IF;
    RETURN NEW;
END;
$$
 LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION create_banner_version()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO banners_banner (
        uuid, id, feature_id_id, content, is_active, created_at, updated_at, previous_version_uuid
    ) 
    VALUES (
    	generate_uuid(),
    	OLD.id,
        NEW.feature_id_id,
        NEW.content,
        CASE 
	        WHEN NEW.is_active IS NOT NULL THEN NEW.is_active
	        ELSE NOT OLD.is_active
	    END,
        OLD.created_at, NOW(),
        NEW.uuid
    );

   RETURN NULL;
END;
$$
 LANGUAGE plpgsql;



CREATE OR REPLACE TRIGGER create_banner_version
BEFORE UPDATE OF feature_id_id, content
ON banners_banner
FOR ROW
EXECUTE PROCEDURE create_banner_version();

CREATE OR REPLACE TRIGGER set_banner_id
BEFORE INSERT
ON banners_banner
FOR ROW
EXECUTE FUNCTION set_banner_id();