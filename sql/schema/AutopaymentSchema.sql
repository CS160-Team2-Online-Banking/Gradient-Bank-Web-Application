USE online_banking;

/*-------------------------------------------------------------------------------------------------
 +	Autopayment Objects
 +  All autopayments are stored as autopayment objects. These records contain information on where
 +  money should be transfered to and from, and what user created the autopayment object. Because
 +  all autopayment objects are intrinsically related to a user account, this table uses a
 +  composite primary key consisting of a user_id and an autopayment id for the given user.
 +  
 +  Scheduling information is stored in a seperate table.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE autopayment_objects (
	owner_user_id INT NOT NULL,
	autopayment_id INT NOT NULL,
	payment_schedule_id INT NOT NULL,
	from_account_id INT NOT NULL, -- this should be owned by the autopayment owner
	to_account_id INT NOT NULL,
	transfer_amount DECIMAL(18,2) NOT NULL,
	PRIMARY KEY (owner_user_id, autopayment_id)
);


/*-------------------------------------------------------------------------------------------------
 +	Payment Schedules
 +  A payment schedule describes when auto payments are to be made. This table is used in
 +  in conjunction with the autopayment objects table to create create transfer requests on time
 +  automatically for a customer.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE payment_schedules (
	schedule_id INT NOT NULL AUTO_INCREMENT,
	start_date DATE NOT NULL,
	end_date DATE NOT NULL,
	payment_frequency ENUM ('YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY') NOT NULL,
	PRIMARY KEY (schedule_id)
);