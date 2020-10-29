USE online_banking;

/*-------------------------------------------------------------------------------------------------
 +	Transfers
 +	All all transfer data will be stored in this table. this includes creation timestamps, a link
 +  to an event log entry, and the amount of money which will be transfered. The transfer type
 +  Enum will be used by the transfer processing system to determine which subrutines should be
 +  used to transfer the money.
 +  For the enums; U_TO_U for user-to-user, A_TO_A for account-to-account
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE transfers (
	transfer_id INT NOT NULL AUTO_INCREMENT,
	create_event_id INT NOT NULL,
	to_account_id INT NOT NULL,
	from_account_id INT NOT NULL,
	transfer_type ENUM ('U_TO_U', 'A_TO_A', 'EXTERN') NOT NULL,
	amount DECIMAL(18,2) NOT NULL,
	time_stamp DATETIME NOT NULL,
	PRIMARY KEY (transfer_id)
);

/*-------------------------------------------------------------------------------------------------
 +	Complete Transfers Log
 +	All transfers remain in the transfers table, but the complete transfers log table can be used
 +	to acces only transfers which have been processed. The primary key must for this table must
 +  also match some value in transfers.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE completed_transfers_log (
	transfer_id INT NOT NULL, -- this should also be in transfers table
	completed DATETIME NOT NULL,
	started DATETIME NOT NULL,
	PRIMARY KEY (transfer_id)
);

/*-------------------------------------------------------------------------------------------------
 +	Pending Transfers Queue
 +	This table will serve as a queue for our transfer processor, and many entries will be added
 +  and deleted from it over time. As such, the pending transfer queue will contain only a time
 +  -stamp for when a transfer was added. The transfer_id should exist in transfers table.
 + 
 +  All entries removed from this table should either have been canceled or moved to the completed
 +  transfers table above.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE pending_transfers_queue (
	transfer_id INT NOT NULL,
	added DATETIME NOT NULL,
	PRIMARY KEY (transfer_id)
);

/*-------------------------------------------------------------------------------------------------
 +	Event Log
 +	The event log will hold information regarding who is editing/adding transfer requests. If a
 +  user requested money to be transfered, then the IP they made that request from will be recorded
 +  in the event queue, as well as the time the request was made. 
 + 
 +  Event Types is a supporting table which holds names and descriptions for the event types,
 +  and below we add two default event types for adding and canceling transfer requests.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE event_log (
	event_id INT NOT NULL AUTO_INCREMENT,
	intiator_user_id INT NOT NULL,
	ip6_address BINARY(16),
	ip4_address BINARY(4),
	event_type INT NOT NULL,
	event_time DATETIME NOT NULL,
	PRIMARY KEY (event_id)
);

CREATE TABLE event_types (
	event_type_id INT NOT NULL AUTO_INCREMENT,
	name VARCHAR(32) UNIQUE NOT NULL,
	descrp VARCHAR(128),
	PRIMARY KEY (event_type_id)
);

INSERT INTO event_types (name, descrp)
VALUES 
	('TRANSFER QUEUED', 'User added a transfer requests to the pending queue.'),
	('TRANSFER CANCELED', 'User canceled a transfer requests in the pending queue.');
	
	
/*-------------------------------------------------------------------------------------------------
 +	Transactions
 +	Transactions are similar to external transfer requests in that they pertain to transfering
 +  money from an internal account to an external. However, transactions are initiated by an
 +  account holder whenever they swipe a credit or debit card associated with a checking or credit
 +  account. Furthermore, they rely on external payment networks to process send the money to a
 +  a merchant who the customer bought something from.
 +  
 +  Similar to transfers, transactions will contain records of all past and present transactions,
 +  including pending transactions.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE transactions (
	transaction_id INT NOT NULL AUTO_INCREMENT,
	card_account_id INT NOT NULL,
	merchant_id INT NOT NULL,
	card_network_id INT NOT NULL,
	amount DECIMAL(18, 2) NOT NULL,
	time_stamp DATETIME NOT NULL,
	PRIMARY KEY (transaction_id)
);

/*-------------------------------------------------------------------------------------------------
 +	Pending Transactions Queue & Completed Transactions Log
 +	This table plays the same role to transaction processing as the pending transfers table does to
 +  transfer processing. Transactions are added/removed as they are processed, and are moved from
 +  this table to the tranasaction log table upon completion. A completion datetime is added
 +  to once the record has been moved.
 *-------------------------------------------------------------------------------------------------*/
CREATE TABLE pending_transactions_queue (
	transaction_id INT NOT NULL,
	added DATETIME NOT NULL,
	PRIMARY KEY (transaction_id)
);
CREATE TABLE completed_transactions_log (
	transaction_id INT NOT NULL,
	started DATETIME NOT NULL,
	completed DATETIME NOT NULL,
	PRIMARY KEY (transaction_id)
);



