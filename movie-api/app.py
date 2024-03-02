from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import difflib
import uvicorn
from joblib import load

app = FastAPI()
movies_data = pd.read_csv('movies.csv')
templates = Jinja2Templates(directory="templates")

similarity = load('similariity.joblib')

def sort_similar_movies(movie_name):
    i = 1
    movies=[]
    
    list_of_all_titles = movies_data['title'].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
    close_match = find_close_match[0]
    index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True) 

    for movie in sorted_similar_movies:
      index = movie[0]
      title_from_index = movies_data[movies_data.index==index]['title'].values[0]
      if (i<30):
        movies.append(title_from_index)
        i+=1

    return movies

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_form")
async def process_form(movie_name: str = Form(...)):
    similar_movies = sort_similar_movies(movie_name)
    return similar_movies

if __name__ == "__main__": 
    uvicorn.run(app, host='localhost', port=8000)