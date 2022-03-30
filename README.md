# tesla-solar-optimiser
Optimises the charging of your Tesla by only charging when there is excess solar through your Powerwall

# Getting Started

Install the python requirements
```
pip install -r requirements
```

Launch the Web Server and the Optimiser with your Tesla username
```
python tso.py myusernamefortesla@mydomain.com --server --optimiser
```

If not already logged in you will be prompted to click a url link. Login at Tesla and the copy the redirect
url back into the console. This has the auth token and will be stored for future logins.


Install React depenedencies
```
npm install
```

Start the React frontend locally
```
npm start
```