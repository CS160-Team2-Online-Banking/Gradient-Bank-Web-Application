USE BankDatabase;
--USE online_banking_playground1;
-- ------------------------------------------------------------------------------------------
-- Table `Accounts`
-- Holds user accounts
-- Account id for internal use, primary key
-- Balance is the account holder's available funds
-- Account number is the actual account number used for transfers, payments, etc.
-- ------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Accounts` (
  `account_id` INT NOT NULL AUTO_INCREMENT,
  `balance` DECIMAL NOT NULL,
  `account_number` INT NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE INDEX `account_number_UNIQUE` (`account_number` ASC) VISIBLE
);


-- ------------------------------------------------------------------------------------------
-- Table `Bank_Manager`
-- Holds the login information for bank mananger
-- Bank manager id for internal use, primary key
-- Hashed pass is the hashed password saved into the database, hash generated elsewhere
-- Manager email for the login field, should be unique
-- ------------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Bank_Manager` (
  `bank_manager_id` INT NOT NULL AUTO_INCREMENT,
  `hashed_pass` VARCHAR(100) NOT NULL,
  `manager_email` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`bank_manager_id`),
  UNIQUE INDEX `manager_email_UNIQUE` (`manager_email` ASC) VISIBLE
);

