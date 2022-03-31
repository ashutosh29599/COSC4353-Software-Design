--
-- PostgreSQL database dump
--

-- Dumped from database version 12.10
-- Dumped by pg_dump version 12.10

-- Started on 2022-03-31 17:05:45

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 202 (class 1259 OID 16433)
-- Name: customer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer (
    customerid character varying(16) NOT NULL,
    customername character varying(50),
    username character varying(20) NOT NULL,
    password character varying(75) NOT NULL
);


ALTER TABLE public.customer OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 16438)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    orderid character varying(16) NOT NULL,
    customerid character varying(16),
    custlocation character varying(30),
    gallonsrequested integer,
    dateofrequest timestamp without time zone,
    price integer
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 16448)
-- Name: user_details; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_details (
    uid character varying(16) NOT NULL,
    customerid character varying(16) NOT NULL,
    cust_name character varying(50),
    address1 character varying(100),
    address2 character varying(100),
    city character varying(100),
    state_ character varying(2),
    zipcode character varying(9)
);


ALTER TABLE public.user_details OWNER TO postgres;

--
-- TOC entry 2694 (class 2606 OID 16437)
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (customerid);


--
-- TOC entry 2696 (class 2606 OID 16442)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (orderid);


--
-- TOC entry 2698 (class 2606 OID 16452)
-- Name: user_details user_details_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_details
    ADD CONSTRAINT user_details_pkey PRIMARY KEY (uid);


--
-- TOC entry 2699 (class 2606 OID 16443)
-- Name: orders orders_customerid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customerid_fkey FOREIGN KEY (customerid) REFERENCES public.customer(customerid);


--
-- TOC entry 2700 (class 2606 OID 16453)
-- Name: user_details user_details_customerid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_details
    ADD CONSTRAINT user_details_customerid_fkey FOREIGN KEY (customerid) REFERENCES public.customer(customerid);


-- Completed on 2022-03-31 17:05:45

--
-- PostgreSQL database dump complete
--

