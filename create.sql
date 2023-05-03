-- Table: public.qna

-- DROP TABLE IF EXISTS public.qna;

CREATE TABLE IF NOT EXISTS public.qna
(
    id integer NOT NULL DEFAULT nextval('qna_id_seq'::regclass),
    article_id integer NOT NULL,
    menu_id integer NOT NULL,
    question character varying(500) COLLATE pg_catalog."default" NOT NULL,
    answer character varying(500) COLLATE pg_catalog."default" NOT NULL,
    q_mbti character(4) COLLATE pg_catalog."default",
    a_mbti character(4) COLLATE pg_catalog."default",
    CONSTRAINT qna_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.qna
    OWNER to postgres;