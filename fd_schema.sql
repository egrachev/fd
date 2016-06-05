--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.3
-- Dumped by pg_dump version 9.5.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: feature; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE feature (
    id integer NOT NULL,
    x1 integer NOT NULL,
    y1 integer NOT NULL,
    x2 integer NOT NULL,
    y2 integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    type integer NOT NULL,
    session integer NOT NULL,
    parent integer
);


ALTER TABLE feature OWNER TO postgres;

--
-- Name: feature_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE feature_id_seq OWNER TO postgres;

--
-- Name: feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE feature_id_seq OWNED BY feature.id;


--
-- Name: featureoverlay; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE featureoverlay (
    id integer NOT NULL,
    feature integer NOT NULL,
    "overlay" integer NOT NULL,
    "position" integer NOT NULL,
    scale double precision NOT NULL
);


ALTER TABLE featureoverlay OWNER TO postgres;

--
-- Name: featureoverlay_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE featureoverlay_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE featureoverlay_id_seq OWNER TO postgres;

--
-- Name: featureoverlay_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE featureoverlay_id_seq OWNED BY featureoverlay.id;


--
-- Name: featuretype; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE featuretype (
    id integer NOT NULL,
    name text NOT NULL,
    color text NOT NULL
);


ALTER TABLE featuretype OWNER TO postgres;

--
-- Name: featuretype_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE featuretype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE featuretype_id_seq OWNER TO postgres;

--
-- Name: featuretype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE featuretype_id_seq OWNED BY featuretype.id;


--
-- Name: overlay; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "overlay" (
    id integer NOT NULL,
    name text NOT NULL,
    image text NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    type integer NOT NULL
);


ALTER TABLE "overlay" OWNER TO postgres;

--
-- Name: overlay_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE overlay_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE overlay_id_seq OWNER TO postgres;

--
-- Name: overlay_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE overlay_id_seq OWNED BY "overlay".id;


--
-- Name: photo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE photo (
    id integer NOT NULL,
    date_create timestamp without time zone DEFAULT now() NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    file_origin text NOT NULL,
    file_path text NOT NULL,
    file_id text NOT NULL
);


ALTER TABLE photo OWNER TO postgres;

--
-- Name: photo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE photo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE photo_id_seq OWNER TO postgres;

--
-- Name: photo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE photo_id_seq OWNED BY photo.id;


--
-- Name: session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE session (
    id integer NOT NULL,
    date_create timestamp without time zone DEFAULT now() NOT NULL,
    name text NOT NULL,
    chat_id integer NOT NULL,
    status integer NOT NULL,
    photo integer,
    "user" integer NOT NULL
);


ALTER TABLE session OWNER TO postgres;

--
-- Name: session_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE session_id_seq OWNER TO postgres;

--
-- Name: session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE session_id_seq OWNED BY session.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE "user" (
    id integer NOT NULL,
    date_create timestamp without time zone DEFAULT now() NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    username text NOT NULL
);


ALTER TABLE "user" OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE user_id_seq OWNED BY "user".id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY feature ALTER COLUMN id SET DEFAULT nextval('feature_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featureoverlay ALTER COLUMN id SET DEFAULT nextval('featureoverlay_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featuretype ALTER COLUMN id SET DEFAULT nextval('featuretype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "overlay" ALTER COLUMN id SET DEFAULT nextval('overlay_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY photo ALTER COLUMN id SET DEFAULT nextval('photo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY session ALTER COLUMN id SET DEFAULT nextval('session_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);


--
-- Name: feature_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY feature
    ADD CONSTRAINT feature_pkey PRIMARY KEY (id);


--
-- Name: featureoverlay_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featureoverlay
    ADD CONSTRAINT featureoverlay_pkey PRIMARY KEY (id);


--
-- Name: featuretype_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featuretype
    ADD CONSTRAINT featuretype_pkey PRIMARY KEY (id);


--
-- Name: overlay_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "overlay"
    ADD CONSTRAINT overlay_pkey PRIMARY KEY (id);


--
-- Name: photo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY photo
    ADD CONSTRAINT photo_pkey PRIMARY KEY (id);


--
-- Name: session_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY session
    ADD CONSTRAINT session_name_key UNIQUE (name);


--
-- Name: session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: idx_feature__parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feature__parent ON feature USING btree (parent);


--
-- Name: idx_feature__session; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feature__session ON feature USING btree (session);


--
-- Name: idx_feature__type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feature__type ON feature USING btree (type);


--
-- Name: idx_featureoverlay__feature; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_featureoverlay__feature ON featureoverlay USING btree (feature);


--
-- Name: idx_featureoverlay__overlay; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_featureoverlay__overlay ON featureoverlay USING btree ("overlay");


--
-- Name: idx_overlay__type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_overlay__type ON "overlay" USING btree (type);


--
-- Name: idx_session__photo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_session__photo ON session USING btree (photo);


--
-- Name: idx_session__user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_session__user ON session USING btree ("user");


--
-- Name: fk_feature__session; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY feature
    ADD CONSTRAINT fk_feature__session FOREIGN KEY (session) REFERENCES session(id);


--
-- Name: fk_feature__type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY feature
    ADD CONSTRAINT fk_feature__type FOREIGN KEY (type) REFERENCES featuretype(id);


--
-- Name: fk_featureoverlay__feature; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featureoverlay
    ADD CONSTRAINT fk_featureoverlay__feature FOREIGN KEY (feature) REFERENCES feature(id);


--
-- Name: fk_featureoverlay__overlay; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY featureoverlay
    ADD CONSTRAINT fk_featureoverlay__overlay FOREIGN KEY ("overlay") REFERENCES "overlay"(id);


--
-- Name: fk_overlay__type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY "overlay"
    ADD CONSTRAINT fk_overlay__type FOREIGN KEY (type) REFERENCES featuretype(id);


--
-- Name: fk_session__photo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY session
    ADD CONSTRAINT fk_session__photo FOREIGN KEY (photo) REFERENCES photo(id);


--
-- Name: fk_session__user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY session
    ADD CONSTRAINT fk_session__user FOREIGN KEY ("user") REFERENCES "user"(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

