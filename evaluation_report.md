# Evaluation Report

## Execution status

The live 11-question evaluation has not yet been run. It needs a reachable Neo4j
database and a valid Gemini API key; running it sends requests to Google and may
incur API charges. After rotating any key previously shared in chat, run:

```powershell
python main.py --eval
```

The command writes measured answers, expected and actual retrievers, a keyword
fact check, and response time for every question to `evaluation_report.csv`.
The fact check is a quick automated signal. Manually review answer relevance
and note at least three good examples and two examples needing improvement
before treating this report as a completed live evaluation.

## Offline regression checks

The local automated tests cover empty query validation, helpful handling of
empty retrievals, unknown graph entities, and evaluation-report generation.
They do not make network calls:

```powershell
python -m unittest discover -s tests -v
```

## Live evaluation questions

| # | Question | Expected path | Expected outcome |
|---|---|---|---|
| 1 | Who acted in The Matrix? | Graph | Cast names from the graph |
| 2 | What movies has Tom Hanks appeared in? | Graph | Filmography from the graph |
| 3 | Who directed Inception? | Graph | Christopher Nolan |
| 4 | Who has Keanu Reeves acted with? | Graph | Co-actors from multi-hop traversal |
| 5 | What films did Christopher Nolan direct? | Graph | The Dark Knight and Inception |
| 6 | Who directed Avatar? | Graph | Helpful no-match response |
| 7 | Recommend a sci-fi movie involving space or advanced technology. | Vector | Science-fiction recommendation |
| 8 | Find me a movie about survival in extreme isolation. | Vector | Cast Away or similarly relevant result |
| 9 | I want to watch something romantic and emotional. | Vector | Titanic or similarly relevant result |
| 10 | Tell me about a film involving crime and moral dilemmas. | Vector | Training Day or similarly relevant result |
| 11 | Suggest a mind-bending movie with an unusual narrative structure. | Vector | The Matrix or Inception |
