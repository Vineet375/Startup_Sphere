import os

file_path = 'templates/incubator/evaluation_list.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_row = """<div class="row text-center mb-3 g-2">
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Innovation</small><strong class="fs-5">{{ eval.innovation_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Market</small><strong class="fs-5">{{ eval.market_potential_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Business</small><strong class="fs-5">{{ eval.business_model_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Team</small><strong class="fs-5">{{ eval.team_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Execution</small><strong class="fs-5">{{ eval.execution_score }}</strong></div></div>
                        </div>"""

new_row = """<div class="row row-cols-2 row-cols-md-5 text-center mb-3 g-2">
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Innovation</small><strong class="fs-5">{{ eval.innovation_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Market</small><strong class="fs-5">{{ eval.market_potential_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Business</small><strong class="fs-5">{{ eval.business_model_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Team</small><strong class="fs-5">{{ eval.team_score }}</strong></div></div>
                            <div class="col"><div class="p-2 bg-light rounded"><small class="d-block text-muted">Execution</small><strong class="fs-5">{{ eval.execution_score }}</strong></div></div>
                        </div>"""

if old_row in content:
    content = content.replace(old_row, new_row)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
