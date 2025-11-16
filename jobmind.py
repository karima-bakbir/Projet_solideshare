from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Données simulées
jobs = [
    {"id": 1, "title": "Data Analyst", "company": "BNP Paribas", "location": "Casablanca, Maroc", "source": "LinkedIn"},
    {"id": 2, "title": "Financial Data Scientist", "company": "Société Générale", "location": "Paris, France", "source": "Indeed"},
    {"id": 3, "title": "Développeur Web", "company": "Startup Maroc", "location": "Rabat, Maroc", "source": "MarocAnnonces"},
]

# Endpoint API pour récupérer les offres
@app.route("/jobs", methods=["GET"])
def get_jobs():
    country = request.args.get("country")
    if country:
        filtered = [job for job in jobs if country.lower() in job["location"].lower()]
        return jsonify(filtered)
    return jsonify(jobs)

# Endpoint API pour rechercher par mot-clé
@app.route("/jobs/search", methods=["GET"])
def search_jobs():
    q = request.args.get("q", "").lower()
    filtered = [job for job in jobs if q in job["title"].lower() or q in job["company"].lower()]
    return jsonify(filtered)

# Page principale HTML + JS + CSS intégrés
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="UTF-8">
      <title>JobMind</title>
      <style>
        body { margin:0; font-family: Poppins,sans-serif; background: #f0f8ff; padding:2rem; }
        h1 { text-align:center; color:#0284c7; font-size:3rem; margin-bottom:1rem; }
        p { text-align:center; color:#475569; margin-bottom:2rem; }
        input, select { padding:0.8rem; border-radius:1.5rem; border:1px solid #cbd5e1; flex:1; }
        button { padding:0.8rem 1.5rem; border-radius:1.5rem; background:#0284c7; color:#fff; border:none; cursor:pointer; }
        .search-container { display:flex; justify-content:center; gap:1rem; margin-bottom:2rem; max-width:700px; margin-left:auto;margin-right:auto; }
        .job-card { padding:1rem; border-radius:1rem; border:1px solid #cbd5e1; background:#fff; box-shadow:0 2px 5px rgba(0,0,0,0.05); margin-bottom:1rem; }
        .job-card h2 { color:#0369a1; font-size:1.3rem; margin-bottom:0.3rem; }
        .job-card p { margin:0.2rem 0; }
        .job-card span { color:#0284c7; font-size:0.8rem; }
      </style>
    </head>
    <body>
      <h1>JobMind</h1>
      <p>Trouvez et postulez automatiquement aux meilleures offres au Maroc et en France.</p>

      <div class="search-container">
        <input type="text" id="query" placeholder="Mot-clé poste ou entreprise...">
        <select id="country">
          <option value="">Tous pays</option>
          <option value="Maroc">Maroc</option>
          <option value="France">France</option>
        </select>
        <button onclick="fetchJobs()">Rechercher</button>
      </div>

      <div id="jobs-container" style="max-width:700px;margin:0 auto;"></div>

      <script>
        async function fetchJobs() {
          const query = document.getElementById('query').value;
          const country = document.getElementById('country').value;
          let url = '/jobs';
          if(query) url = '/jobs/search?q=' + encodeURIComponent(query);
          if(country) url += query ? '&country=' + encodeURIComponent(country) : '?country=' + encodeURIComponent(country);
          const container = document.getElementById('jobs-container');
          container.innerHTML = '<p style="text-align:center;color:#0284c7;">Chargement...</p>';
          try {
            const res = await fetch(url);
            const data = await res.json();
            if(data.length === 0){
              container.innerHTML = '<p style="text-align:center;color:#0284c7;">Aucune offre trouvée.</p>';
              return;
            }
            container.innerHTML = '';
            data.forEach(job => {
              const card = document.createElement('div');
              card.className = 'job-card';
              card.innerHTML = `
                <h2>${job.title}</h2>
                <p>Entreprise: ${job.company}</p>
                <p>Lieu: ${job.location}</p>
                <span>Source: ${job.source}</span>
              `;
              container.appendChild(card);
            });
          } catch(err) {
            console.error(err);
            container.innerHTML = '<p style="text-align:center;color:red;">Erreur lors de la récupération des offres.</p>';
          }
        }
      </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    print("JobMind full stack sur http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

