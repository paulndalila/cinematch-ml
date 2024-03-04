from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import difflib
import uvicorn
from joblib import load
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="statics"), name="static")

similarity = load('similariity.joblib')
movies_data = pd.read_csv('movies.csv')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_form")
async def process_form(request: Request, movie_name: str = Form(...)):
    i = 1
    movies=[]
    close_matches_with_overviews = []
    
    list_of_all_titles = movies_data['title'].tolist()
    find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
    
    for close_match in find_close_match:
        overview = movies_data[movies_data.title == close_match]['overview'].values[0]
        close_matches_with_overviews.append({"title": close_match, "overview": overview})
        
    close_match = find_close_match[0]
    index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values[0]
    similarity_score = list(enumerate(similarity[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key = lambda x:x[1], reverse = True) 

    for movie in sorted_similar_movies:
      index = movie[0]
      title_from_index = movies_data[movies_data.index==index]['title'].values[0]
      overview_from_index = movies_data[movies_data.index == index]['overview'].values[0]
      if (i<30):
        movies.append({"title":title_from_index, "overview": overview_from_index})
        i+=1

    similar_movies = movies
    #return similar_movies
    return templates.TemplateResponse("results.html", {"request": request, "movie_name": movie_name, "similar_movies": list(similar_movies), "close_match": close_matches_with_overviews})

if __name__ == "__main__": 
    uvicorn.run(app, host='localhost', port=8000)