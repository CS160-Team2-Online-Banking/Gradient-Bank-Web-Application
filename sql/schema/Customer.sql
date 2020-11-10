USE online_banking_playground_1;
/*-------------------------------------------------------------------------------------------------
 Customer
 Holds basic information for Customer
 
 customer_id(PK): the unique ID for each Customer
 account_id(FK): the associated account ID
 event_id(FK): the associated EventLog ID
 autopayment_id(FK): the associated Autopayment Object ID
 customer_name: the name of the customer
 customer_phone: the phone number of the customer
 customer_email: the email of the customer
 customer_SSN: the SSN of the customer
 customer_address: the address of the customer
 customer_routingNumber: the routing number of the customer
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE Customer (
	customer_id int NOT NULL,
	account_id int NOT NULL,
	event_id int,
	autopayment_id int,
	customer_password char(256) NOT NULL,
	customer_name char(50) NOT NULL,
    customer_phone int(10) NOT NULL,
    customer_email varchar(50) NOT NULL,
    customer_SSN int(9) NOT NULL,
    customer_address varchar(50) NOT NULL,
    customer_routingNumber int(9) NOT NULL,
	PRIMARY KEY (customer_id)
);