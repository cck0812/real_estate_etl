# real_estate_etl

## Usage

Setup the develop environment.

    docker-compose up -d real-estate-crawler real-estate-api

After the `docker-compose up`, then get the data.

    docker exec crawler python /code/real_estate_handler.py <year:int> <season:int>

E.g., `docker exec crawler python /code/real_estate_handler.py 108 2`

Use the RESTful URL below to get the JSON format data.

    http://127.0.0.1:5000/data/<鄉鎮市區:中文>/<總樓層數:阿拉伯數字>/<建物型態:中文>

E.g., `http://127.0.0.1:5000/data/西區/3/店面`
