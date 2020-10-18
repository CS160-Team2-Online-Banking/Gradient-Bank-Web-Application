USE online_banking_playground_1;

/*
	Below is an example transaction for transfering money between two internal accounts.
    This kind of interaction is a classic example of why transactions are important: they
    ensure that if our database were to crash in the middle of a transaction (possibly right after
    we subtract a quantity from someones account), the transaction is canceled and no one
    loses any money.
    
    I've wrapped the transaction in a procedure for the sake of convenience
*/

DELIMITER //
CREATE PROCEDURE exec_internal_transfer (IN _transfer_id INT)
BEGIN
	DECLARE _from_account_id INT;
    DECLARE _to_account_id INT;
    DECLARE _amount DECIMAL(18,2);
    DECLARE _from_account_balance DECIMAL(18,2) DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION ROLLBACK; -- if we fail and throw an exception, roll back the transaction
	
    START TRANSACTION;
    SELECT from_account_id INTO _from_account_id FROM transfers WHERE transfer_id = _transfer_id;
    SELECT to_account_id INTO _to_account_id FROM transfers WHERE transfer_id = _transfer_id;
    SELECT amount INTO _amount FROM transfers WHERE transfer_id = _transfer_id;
    SELECT
		ISNULL(balance, 0) INTO _from_account_balance
    FROM bank_accounts
    WHERE account_id = _from_account_id;

	-- attempt to transfer the money --
	UPDATE bank_accounts SET balance = balance - amount WHERE account_id = from_account_id;
	UPDATE bank_accounts SET balance = balance + amount WHERE account_id = to_account_id;
    
	IF ((SELECT balance FROM bank_accounts WHERE account_id = from_account_id) < 0) THEN -- if the from account's balance is now negative
		ROLLBACK; -- roll back the transaction, you cannot transfer money you do not have
	ELSE
		COMMIT;
	END IF;
END //
DELIMITER ;

