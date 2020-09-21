# API

api_key = e880cf92
http://www.omdbapi.com/?t=Game%20of%20Thrones&Season=1&apikey=e880cf92

---
To RUN:

1. docker-compose up -d --build
2. docker exec -it flask-app sh  
3. python dbmanager.py db upgrade
4. Head over to -> http://localhost:5000/api/api_documentation.html
5. Use POST /api/shows using "Game of Thrones" to create db entry for show
6. Use POST /api/episodes/{show_id} using the ID for the show (probably 1) to populate episode data (it will take a while)


---
Notes

Happy with the functionality thats there, kinda ran out of time which I would have 
liked to implement testing, nginx and gunicorn, 