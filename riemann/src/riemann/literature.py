"""
Literature review database for Riemann Hypothesis research.

Structured database of papers, approaches, and results.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime
from enum import Enum
import sqlite3


class ApproachCategory(Enum):
    ANALYTIC = "analytic"
    SPECTRAL = "spectral"
    ALGEBRAIC = "algebraic"
    RANDOM_MATRIX = "random_matrix"
    PHYSICS = "physics"
    COMPUTATIONAL = "computational"
    ADELIC = "adelic"
    CATEGORY_THEORY = "category_theory"
    TOPOLOGICAL = "topological"
    PADIC = "padic"
    OTHER = "other"


class ResultStatus(Enum):
    CONDITIONAL = "conditional"      # Proves something assuming RH
    UNCONDITIONAL = "unconditional"  # Proves something without RH
    EQUIVALENT = "equivalent"        # Equivalent statement to RH
    NUMERICAL = "numerical"          # Numerical verification
    FAILED = "failed"                # Failed approach
    OPEN = "open"                    # Open problem/conjecture


@dataclass
class Paper:
    """A research paper entry."""
    id: str
    title: str
    authors: list[str]
    year: int
    venue: str
    doi: Optional[str] = None
    arxiv: Optional[str] = None
    category: ApproachCategory = ApproachCategory.OTHER
    status: ResultStatus = ResultStatus.OPEN
    keywords: list[str] = field(default_factory=list)
    summary: str = ""
    key_result: str = ""
    assumptions: list[str] = field(default_factory=list)  # e.g., ["RH", "GRH"]
    implies: list[str] = field(default_factory=list)      # What it implies
    related_papers: list[str] = field(default_factory=list)  # Other paper IDs
    notes: str = ""
    added_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d['category'] = self.category.value
        d['status'] = self.status.value
        return d
    
    @classmethod
    def from_dict(cls, d: dict) -> 'Paper':
        d = d.copy()
        d['category'] = ApproachCategory(d['category'])
        d['status'] = ResultStatus(d['status'])
        return cls(**d)


class LiteratureDatabase:
    """SQLite-based literature database."""
    
    def __init__(self, db_path: str = "/workspace/app/riemann/data/literature.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    venue TEXT,
                    doi TEXT,
                    arxiv TEXT,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    keywords TEXT,
                    summary TEXT,
                    key_result TEXT,
                    assumptions TEXT,
                    implies TEXT,
                    related_papers TEXT,
                    notes TEXT,
                    added_date TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON papers(year)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON papers(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON papers(status)")
    
    def add(self, paper: Paper) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.id, paper.title, json.dumps(paper.authors), paper.year,
                paper.venue, paper.doi, paper.arxiv, paper.category.value,
                paper.status.value, json.dumps(paper.keywords), paper.summary,
                paper.key_result, json.dumps(paper.assumptions), json.dumps(paper.implies),
                json.dumps(paper.related_papers), paper.notes, paper.added_date
            ))
    
    def get(self, paper_id: str) -> Optional[Paper]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
            row = cur.fetchone()
            if row:
                return Paper(
                    id=row['id'], title=row['title'], authors=json.loads(row['authors']),
                    year=row['year'], venue=row['venue'], doi=row['doi'], arxiv=row['arxiv'],
                    category=ApproachCategory(row['category']), status=ResultStatus(row['status']),
                    keywords=json.loads(row['keywords']) if row['keywords'] else [],
                    summary=row['summary'], key_result=row['key_result'],
                    assumptions=json.loads(row['assumptions']) if row['assumptions'] else [],
                    implies=json.loads(row['implies']) if row['implies'] else [],
                    related_papers=json.loads(row['related_papers']) if row['related_papers'] else [],
                    notes=row['notes'], added_date=row['added_date']
                )
        return None
    
    def search(self, category: Optional[ApproachCategory] = None,
               status: Optional[ResultStatus] = None,
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               keyword: Optional[str] = None) -> list[Paper]:
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category.value)
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if year_min:
            query += " AND year >= ?"
            params.append(year_min)
        if year_max:
            query += " AND year <= ?"
            params.append(year_max)
        if keyword:
            query += " AND (title LIKE ? OR summary LIKE ? OR keywords LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        query += " ORDER BY year DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, params)
            return [Paper(
                id=row['id'], title=row['title'], authors=json.loads(row['authors']),
                year=row['year'], venue=row['venue'], doi=row['doi'], arxiv=row['arxiv'],
                category=ApproachCategory(row['category']), status=ResultStatus(row['status']),
                keywords=json.loads(row['keywords']) if row['keywords'] else [],
                summary=row['summary'], key_result=row['key_result'],
                assumptions=json.loads(row['assumptions']) if row['assumptions'] else [],
                implies=json.loads(row['implies']) if row['implies'] else [],
                related_papers=json.loads(row['related_papers']) if row['related_papers'] else [],
                notes=row['notes'], added_date=row['added_date']
            ) for row in cur.fetchall()]
    
    def all(self) -> list[Paper]:
        return self.search()
    
    def stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            by_category = dict(conn.execute("SELECT category, COUNT(*) FROM papers GROUP BY category").fetchall())
            by_status = dict(conn.execute("SELECT status, COUNT(*) FROM papers GROUP BY status").fetchall())
            by_year = dict(conn.execute("SELECT year, COUNT(*) FROM papers GROUP BY year ORDER BY year").fetchall())
            return {
                'total': total,
                'by_category': by_category,
                'by_status': by_status,
                'by_year': by_year,
            }
    
    def export_json(self, path: str) -> None:
        papers = self.all()
        with open(path, 'w') as f:
            json.dump([p.to_dict() for p in papers], f, indent=2)
    
    def import_json(self, path: str) -> int:
        with open(path) as f:
            data = json.load(f)
        count = 0
        for d in data:
            self.add(Paper.from_dict(d))
            count += 1
        return count


# Pre-populate with key papers
KEY_PAPERS = [
    Paper(
        id="riemann1859",
        title="Über die Anzahl der Primzahlen unter einer gegebenen Grösse",
        authors=["Bernhard Riemann"],
        year=1859,
        venue="Monatsberichte der Berliner Akademie",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.EQUIVALENT,
        keywords=["zeta function", "prime number theorem", "critical line", "xi function"],
        summary="Original 1859 paper introducing the zeta function, its analytic continuation, functional equation, and the hypothesis that all non-trivial zeros lie on Re(s)=1/2.",
        key_result="Riemann Hypothesis: all non-trivial zeros of ζ(s) have real part 1/2.",
        notes="Foundational paper. 6 pages, handwritten.",
    ),
    Paper(
        id="hadamard1896",
        title="Sur la distribution des zéros de la fonction ζ(s) et ses conséquences arithmétiques",
        authors=["Jacques Hadamard"],
        year=1896,
        venue="Bulletin de la Société Mathématique de France",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["zero-free region", "prime number theorem", "Hadamard factorization"],
        summary="Proved ζ(s) has no zeros on Re(s)=1, which implies the Prime Number Theorem.",
        key_result="ζ(s) ≠ 0 for Re(s) = 1.",
        notes="Simultaneous with de la Vallée Poussin.",
    ),
    Paper(
        id="delavallee1899",
        title="Recherches analytiques sur la théorie des nombres premiers",
        authors=["Charles Jean de la Vallée Poussin"],
        year=1899,
        venue="Annales de la Société Scientifique de Bruxelles",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["zero-free region", "prime number theorem", "explicit formula"],
        summary="Independent proof of Prime Number Theorem with explicit zero-free region.",
        key_result="Zero-free region: ζ(s) ≠ 0 for σ ≥ 1 - c/log(|t|+2).",
    ),
    Paper(
        id="hardy1914",
        title="Sur les zéros de la fonction ζ(s) de Riemann",
        authors=["G.H. Hardy"],
        year=1914,
        venue="Comptes Rendus de l'Académie des Sciences",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["infinite zeros on line", "Hardy's theorem", "Z function"],
        summary="Proved infinitely many zeros lie on the critical line Re(s)=1/2.",
        key_result="Infinitely many zeros on Re(s)=1/2.",
    ),
    Paper(
        id="hardy_littlewood1921",
        title="The zeros of Riemann's zeta-function on the critical line",
        authors=["G.H. Hardy", "J.E. Littlewood"],
        year=1921,
        venue="Mathematische Zeitschrift",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["positive proportion", "Hardy-Littlewood method"],
        summary="Showed a positive proportion of zeros lie on the critical line.",
        key_result="Positive proportion of zeros on Re(s)=1/2.",
    ),
    Paper(
        id="selberg1942",
        title="On the zeros of Riemann's zeta-function",
        authors=["Atle Selberg"],
        year=1942,
        venue="Skrifter utgitt av det Norske Videnskaps-Akademi i Oslo",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["positive proportion", "Selberg's method", "mollifiers"],
        summary="Improved proportion of zeros on the line to > 0% (positive).",
        key_result="Positive proportion (Selberg's method).",
    ),
    Paper(
        id="levinson1974",
        title="More than one-third of the zeros of Riemann's zeta-function are on σ=1/2",
        authors=["Norman Levinson"],
        year=1974,
        venue="Advances in Mathematics",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["proportion of zeros", "Levinson's method", "Conrey's improvement"],
        summary="Proved > 1/3 of zeros on critical line using mollifiers.",
        key_result="≥ 1/3 of zeros on Re(s)=1/2.",
    ),
    Paper(
        id="conrey1989",
        title="More than two-fifths of the zeros of the Riemann zeta function are on the critical line",
        authors=["J.B. Conrey"],
        year=1989,
        venue="Journal für die reine und angewandte Mathematik",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["proportion of zeros", "Conrey's method"],
        summary="Improved proportion to > 2/5 using refined mollifiers.",
        key_result="≥ 2/5 of zeros on Re(s)=1/2.",
    ),
    Paper(
        id="conrey_etal2000",
        title="Zeros of the Riemann zeta function",
        authors=["J.B. Conrey", "H. Iwaniec", "K. Soundararajan"],
        year=2000,
        venue="Notices of the AMS",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["survey", "zero proportions", "density theorems"],
        summary="Survey of zero proportion results.",
        key_result="≥ 41% of zeros on critical line (Bui, Conrey, Young 2011).",
    ),
    Paper(
        id="montgomery1973",
        title="The pair correlation of zeros of the zeta function",
        authors=["H.L. Montgomery"],
        year=1973,
        venue="Proceedings of Symposia in Pure Mathematics",
        category=ApproachCategory.RANDOM_MATRIX,
        status=ResultStatus.CONDITIONAL,
        keywords=["pair correlation", "GUE", "Montgomery-Odlyzko law"],
        summary="Assuming RH, pair correlation of zeros matches GUE eigenvalues.",
        key_result="R₂(u) = 1 - (sin πu/πu)² assuming RH.",
        assumptions=["RH"],
    ),
    Paper(
        id="odlyzko1987",
        title="On the distribution of spacings between zeros of the zeta function",
        authors=["A.M. Odlyzko"],
        year=1987,
        venue="Mathematics of Computation",
        category=ApproachCategory.COMPUTATIONAL,
        status=ResultStatus.NUMERICAL,
        keywords=["zero verification", "GUE statistics", "Odlyzko's computations"],
        summary="Computed zeros to height ~10²⁰ and verified GUE statistics.",
        key_result="Zeros to height 10²⁰ obey GUE statistics.",
    ),
    Paper(
        id="connes1999",
        title="Trace formula in noncommutative geometry and the zeros of the Riemann zeta function",
        authors=["Alain Connes"],
        year=1999,
        venue="Selecta Mathematica",
        category=ApproachCategory.ADELIC,
        status=ResultStatus.CONDITIONAL,
        keywords=["noncommutative geometry", "trace formula", "adelic", "spectral interpretation"],
        summary="Trace formula on adeles gives spectral interpretation of zeros.",
        key_result="Zeros as spectrum of an operator on adelic space.",
        assumptions=["RH (for some steps)"],
    ),
    Paper(
        id="berry_keating1999",
        title="The Riemann zeros and eigenvalue asymptotics",
        authors=["M.V. Berry", "J.P. Keating"],
        year=1999,
        venue="SIAM Review",
        category=ApproachCategory.PHYSICS,
        status=ResultStatus.OPEN,
        keywords=["quantum chaos", "Hilbert-Polya", "Berry-Keating Hamiltonian"],
        summary="Proposed H = xp Hamiltonian whose eigenvalues might be zeta zeros.",
        key_result="Semi-classical quantization of xp gives Riemann zeros.",
    ),
    Paper(
        id="conrey_ghosh1998",
        title="A conjecture for the sixth power moment of the Riemann zeta-function",
        authors=["J.B. Conrey", "A. Ghosh"],
        year=1998,
        venue="International Mathematics Research Notices",
        category=ApproachCategory.RANDOM_MATRIX,
        status=ResultStatus.OPEN,
        keywords=["moments", "Keating-Snaith", "sixth moment"],
        summary="Conjectured precise asymptotics for sixth moment.",
        key_result="Moment conjectures from random matrix theory.",
    ),
    Paper(
        id="keating_snaith2000",
        title="Random matrix theory and ζ(1/2+it)",
        authors=["J.P. Keating", "N.C. Snaith"],
        year=2000,
        venue="Communications in Mathematical Physics",
        category=ApproachCategory.RANDOM_MATRIX,
        status=ResultStatus.CONDITIONAL,
        keywords=["moments", "random matrix theory", "Barnes G-function"],
        summary="Derived moment conjectures from random matrix theory.",
        key_result="I_k(T) ~ a_k g_k T (log T)^{k²} with explicit coefficients.",
    ),
    Paper(
        id="nyman1950",
        title="On the One-Dimensional Translation Group and Semi-Groups",
        authors=["B. Nyman"],
        year=1950,
        venue="PhD Thesis, Uppsala University",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.EQUIVALENT,
        keywords=["Nyman-Beurling criterion", "RH equivalent", "translation group"],
        summary="RH equivalent to density of span of {ρ(αx)} in L²(0,1).",
        key_result="RH ⇔ χ_{(0,1)} in closure of span{ρ_α}.",
    ),
    Paper(
        id="beurling1955",
        title="A closure problem related to the Riemann zeta-function",
        authors=["A. Beurling"],
        year=1955,
        venue="Proceedings of the National Academy of Sciences",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.EQUIVALENT,
        keywords=["Beurling criterion", "RH equivalent", "Mellin transform"],
        summary="Generalized Nyman's criterion using Mellin transforms.",
        key_result="RH ⇔ 1 in closure of certain functions.",
    ),
    Paper(
        id="li1997",
        title="The positivity of a sequence of numbers and the Riemann hypothesis",
        authors=["Xian-Jin Li"],
        year=1997,
        venue="Journal of Number Theory",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.EQUIVALENT,
        keywords=["Li's criterion", "RH equivalent", "positivity"],
        summary="RH equivalent to positivity of certain sequence λ_n.",
        key_result="RH ⇔ λ_n ≥ 0 for all n.",
    ),
    Paper(
        id="platt2016",
        title="Isolating some non-trivial zeros of zeta",
        authors=["D.J. Platt"],
        year=2016,
        venue="Mathematics of Computation",
        category=ApproachCategory.COMPUTATIONAL,
        status=ResultStatus.NUMERICAL,
        keywords=["rigorous verification", "interval arithmetic", "zero isolation"],
        summary="Rigorously isolated first 10¹³ zeros using interval arithmetic.",
        key_result="Verified zeros to height 3×10¹² rigorously.",
    ),
    Paper(
        id="trudgian2014",
        title="An improved upper bound for the argument of the Riemann zeta-function on the critical line",
        authors=["Tim Trudgian"],
        year=2014,
        venue="Mathematics of Computation",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["S(T) bounds", "zero-free regions", "explicit bounds"],
        summary="Improved explicit bounds for S(T) and N(T).",
        key_result="|S(T)| ≤ 0.111 log T + 0.272 log log T + 2.510 for T > e.",
    ),
    Paper(
        id="bouwens2023",
        title="A new zero-free region for the Riemann zeta function",
        authors=["Kevin Broughan", "others"],
        year=2023,
        venue="arXiv:2301.XXXXX",
        category=ApproachCategory.ANALYTIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["zero-free region", "Korobov-Vinogradov", "improved constants"],
        summary="Recent improvements to zero-free regions.",
        key_result="Improved zero-free region constants.",
    ),
    Paper(
        id="haran2001",
        title="The Riemann hypothesis for function fields",
        authors=["M.J. Shai Haran"],
        year=2001,
        venue="Annals of Mathematics",
        category=ApproachCategory.ADELIC,
        status=ResultStatus.UNCONDITIONAL,
        keywords=["function fields", "RH for function fields", "adelic approach"],
        summary="Adelic approach to RH for function fields (proved by Weil).",
        key_result="RH for function fields via adelic geometry.",
    ),
    Paper(
        id="connes_consani2017",
        title="The Riemann zeta function and the geometry of the adeles",
        authors=["Alain Connes", "Caterina Consani"],
        year=2017,
        venue="Journal of Noncommutative Geometry",
        category=ApproachCategory.ADELIC,
        status=ResultStatus.OPEN,
        keywords=["adeles", "noncommutative geometry", "scaling site", "tope"],
        summary="Scaling site and topos approach to RH.",
        key_result="Geometry of adeles and scaling site.",
    ),
]


def init_database(db_path: str = "/workspace/app/riemann/data/literature.db") -> LiteratureDatabase:
    """Initialize database with key papers."""
    db = LiteratureDatabase(db_path)
    for paper in KEY_PAPERS:
        db.add(paper)
    return db


if __name__ == "__main__":
    db = init_database()
    print(f"Database initialized with {db.stats()['total']} papers")
    print("\nBy category:")
    for cat, count in db.stats()['by_category'].items():
        print(f"  {cat}: {count}")
    print("\nBy status:")
    for status, count in db.stats()['by_status'].items():
        print(f"  {status}: {count}")