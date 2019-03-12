##### Create and activate virtual environment
```console
$ python3 -m venv ./venv
$ source venv/bin/activate
```

##### Install requirements in venv
```console
$ pip3 install -r requirements.txt
```

##### Update config.py
* add secret keys and database uri

##### Run 
* in venv using:
```console
$ python3 run.py
```
* OR outside of penv using:
```console
$ uwsgi hera_app.ini
```