USE online_banking_playground_1;

/*
	What this trigger does is automatically increment the auto_payment id for w/e the max id is 
    among the autopayment objects owned by our owner.
    
    Solution adapted from noz
    Reference: https://stackoverflow.com/questions/18120088/defining-composite-key-with-auto-increment-in-mysql
*/
DELIMITER //
CREATE TRIGGER ins_autopayment BEFORE INSERT ON autopayment_objects
FOR EACH ROW
BEGIN
	SET NEW.autopayment_id = (SELECT IFNULL(MAX(autopayment_id), -1)+1 -- if no entries are found, simply return -1 + 1 = 0
							  FROM autopayment_objects
                              WHERE owner_user_id = NEW.owner_user_id); 
END;//
DELIMITER ;