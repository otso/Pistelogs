curl -d "user_id=john" -d "run_guid={a5fe9b99-6d6a-456f-9b2c-19e3c991f6b3}" -d @raw_log_3.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=john" -d "run_guid={a5fe9b99-6d6a-456f-9b2c-19e3c991f6b3}" -d @raw_log_4.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=john" -d "run_guid={25fe9b99-6d6a-456f-9b2c-19e3c991f6b2}" -d @raw_log_1.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=john" -d "run_guid={55fe9b99-6d6a-456f-9b2c-19e3c991f6b5}" -d @raw_log_2.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy

curl -d "user_id=mike" -d "run_guid={55fe9b99-6d6a-456f-9b2c-19e3c991f6a5}" -d @raw_log_2.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=jake" -d "run_guid={55fe9b99-6d6a-456f-9b2c-19e3c991f6c5}" -d @raw_log_2.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=jane" -d "run_guid={55fe9b99-6d6a-456f-9b2c-19e3c991f6d5}" -d @raw_log_2.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy
curl -d "user_id=zoee" -d "run_guid={55fe9b99-6d6a-456f-9b2c-19e3c991f6e5}" -d @raw_log_2.txt http://pistelogs.appspot.com/api/depositlog -v -x $http_proxy

