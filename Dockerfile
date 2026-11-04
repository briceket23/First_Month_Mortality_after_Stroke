FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra texlive-bibtex-extra poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY . /work
RUN pip install --no-cache-dir -r requirements.lock && python scripts/make_synthetic_fixture.py
# real data: docker run -v /secure/db.xlsx:/data/db.xlsx -e STROKE_DATA_PATH=/data/db.xlsx image python run_all.py --mode all --accept-provisional --clean
CMD ["sh", "-c", "STROKE_SYNTHETIC=1 python run_all.py --mode all --accept-provisional --quick --clean"]
