

## Pricer

This program downloads prices from different cryptocurrency exchanges and stores them in a database


### Prerequisites

* MySQL Server
* Python 3
* pipenv


### Configuration


* In the root of the folder run the next command to install the python library and generate a virtual environment

    <pre> pipenv install --three </pre>

* Create a database in MySQL with the name pricer

* Load database :

    <pre> mysql -u USER_NAME -p  pricer <  db/create.sql </pre>



### Run the program


* Modify  the file code/params.txt and inlude the host names, notification email address and resources of the files you want to download


* To start the program execute the file:

    <pre> start.sh  </pre>

### Note

Works only with Bitfinex, Bitso and Binance
