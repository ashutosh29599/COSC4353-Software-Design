PGDMP                         z           fuel_app    12.10    12.10                0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    16400    fuel_app    DATABASE     �   CREATE DATABASE fuel_app WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'English_United States.1252' LC_CTYPE = 'English_United States.1252';
    DROP DATABASE fuel_app;
                postgres    false                       0    0    DATABASE fuel_app    COMMENT     4   COMMENT ON DATABASE fuel_app IS 'COSC4353 Project';
                   postgres    false    2836                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
                postgres    false                       0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                   postgres    false    3            �            1259    16433    customer    TABLE     �   CREATE TABLE public.customer (
    customerid character varying(16) NOT NULL,
    customername character varying(50),
    username character varying(20) NOT NULL,
    password character varying(75) NOT NULL
);
    DROP TABLE public.customer;
       public         heap    postgres    false    3            �            1259    16438    orders    TABLE     &  CREATE TABLE public.orders (
    orderid character varying(16) NOT NULL,
    customerid character varying(16),
    custlocation character varying(200),
    gallonsrequested integer,
    dateofrequest timestamp without time zone,
    deliverydate date,
    price_p_gal money,
    price money
);
    DROP TABLE public.orders;
       public         heap    postgres    false    3            �            1259    16448    user_details    TABLE     O  CREATE TABLE public.user_details (
    uid character varying(16) NOT NULL,
    customerid character varying(16) NOT NULL,
    cust_name character varying(50),
    address1 character varying(100),
    address2 character varying(100),
    city character varying(100),
    state_ character varying(2),
    zipcode character varying(9)
);
     DROP TABLE public.user_details;
       public         heap    postgres    false    3                      0    16433    customer 
   TABLE DATA           P   COPY public.customer (customerid, customername, username, password) FROM stdin;
    public          postgres    false    202   �                 0    16438    orders 
   TABLE DATA           �   COPY public.orders (orderid, customerid, custlocation, gallonsrequested, dateofrequest, deliverydate, price_p_gal, price) FROM stdin;
    public          postgres    false    203   �                 0    16448    user_details 
   TABLE DATA           m   COPY public.user_details (uid, customerid, cust_name, address1, address2, city, state_, zipcode) FROM stdin;
    public          postgres    false    204   8       �
           2606    16437    customer customer_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (customerid);
 @   ALTER TABLE ONLY public.customer DROP CONSTRAINT customer_pkey;
       public            postgres    false    202            �
           2606    16442    orders orders_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (orderid);
 <   ALTER TABLE ONLY public.orders DROP CONSTRAINT orders_pkey;
       public            postgres    false    203            �
           2606    16452    user_details user_details_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.user_details
    ADD CONSTRAINT user_details_pkey PRIMARY KEY (uid);
 H   ALTER TABLE ONLY public.user_details DROP CONSTRAINT user_details_pkey;
       public            postgres    false    204            �
           2606    16443    orders orders_customerid_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customerid_fkey FOREIGN KEY (customerid) REFERENCES public.customer(customerid);
 G   ALTER TABLE ONLY public.orders DROP CONSTRAINT orders_customerid_fkey;
       public          postgres    false    203    202    2695            �
           2606    16453 )   user_details user_details_customerid_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_details
    ADD CONSTRAINT user_details_customerid_fkey FOREIGN KEY (customerid) REFERENCES public.customer(customerid);
 S   ALTER TABLE ONLY public.user_details DROP CONSTRAINT user_details_customerid_fkey;
       public          postgres    false    202    204    2695               "  x�E�Iv�0  �5�õ5 K0(2�`�u�2D�0��]Y��Z�*��b�+� �0ɀ��Y��JW_�LU2x
؃��#Ʌ/*��M����͒��Z��5]Y�9� 2ga'|^�W8�w�ڔ��s��s9T*Er�p���~t\W<p�s�H�;�ۅ%�h�$��:pX�X��E:twjm�f���ި���4ފ��Uf�#���t-OoƸh	[�#��OT&r)���E/\u�;6+/�A����]�3�	a^Q�̊'��dc_mCr����� fOٟ5˲R�r�         p  x���[o�@�g����)9scް�R��ծ�f_�Q�(b/~�بTl6ٚ�����?gZk{]�F�6��,L�w�N��͐���h���|��ȋ��0rW���K��,�1zb$%�4( ����/)A��L]�K%゘R��L��N�`zߚ��p��U� �=^&i,P#�K��򬅈���#�i[�Hz,���łSS@-k�����=����ޮZe��d�(M��5#:0(a=� �L�ڒ�|���2�3�����0d�fv�kT�V��,�GH/���VD�^a+aXgLCL�@rr,Y{!H�p�3ϋ�x��a�;?�.�/�BN��(��Q�
l�T������H��������7��.����G�¨�bt�/!�n���A:B��PL��0�Ѱ�EE>��C����OܛH���� �F��?`+�'�A�����g����M�Ij̯� ]w���{ҝ��"���(9���`�Q���ŹX�(T*���=�y,)vv����v��O��A��G��S��!�
NJ�"�XzB���/朁�A:���f£���ߜ�-a��\��d8��IeŤ�Ų<ήf^'݌<�x��1��rt��X�(-~��Z��lcT         �   x�]���  ���S�MIf�ԭ�5�䡋n����ӷ����'���8��%tld��iC:/��n���Ym�s��!\E�rJ�W��b�,��PJH��c��&4�l��g0&wo�.6]���??��v8O��m�B�
�u��7?N6B     