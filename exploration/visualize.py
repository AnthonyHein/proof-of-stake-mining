from datetime import datetime
import dill
import html
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from typing import List

# plt.rcParams["figure.figsize"] = [3, 2]

from cell import Cell

PATH_TO_CSV_DIR = "temp/csv/"
PATH_TO_HTML_DIR = "temp/html/"

def save(settings, table: List[Cell]) -> None:
    """
    Save a `table` created under `settings` as a `.csv` and
    `.html` file for ease of comprehension and visualization.
    """

    if settings["visualization"] == "csv":
        _save_csv(settings, table)
    elif settings["visualization"] == "table":
        _save_html_table(settings, table)
    elif settings["visualization"] == "cards":
        _save_html_cards(settings, table)
    else:
        print(f"visualize.save: didn't recognize visualization settings {settings['visualization']}")
        sys.exit(1)

def _save_csv(settings, table: List[Cell]) -> None:
    """
    Save a `table` created under `settings` as a `.csv` for ease of
    comprehension and visualization.
    """

    f = open(PATH_TO_CSV_DIR + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv", "w")

    for key in settings:
        f.write(f"settings['{key}'],{settings[key]},,,,,,\n")

    f.write(f"id,state,lb_lemma,lb_str,ub_lemma,ub_str,lb_fn,ub_fn\n")

    for cell in table:
        if cell is not None:
            f.write(
                f"\"{str(int(cell.get_state()))}\"," +
                f"\"{str(cell.get_state())}\"," +
                f"\"{str(cell.get_lb_lemma())}\"," +
                f"\"{str(cell.get_lb_str())}\"," +
                f"\"{str(cell.get_ub_lemma())}\"," +
                f"\"{str(cell.get_ub_str())}\"," +
                f"\"{str(dill.dumps(cell.get_lb_fn()))}\"," +
                f"\"{str(dill.dumps(cell.get_ub_fn()))}\"\n"
            )

    f.close()

def _save_html_table(settings, table: List[Cell]) -> None:
    """
    Save a `table` created under `settings` as a `.html` for ease of
    comprehension and visualization.
    """

    filename = datetime.now().strftime("%Y%m%d%H%M%S")

    os.mkdir(PATH_TO_HTML_DIR + filename + "/")
    f = open(PATH_TO_HTML_DIR + filename + "/" + filename + ".html", "w")

    f.write(f"<html>\n")
    f.write(f"\t<head>\n")
    f.write(f"\t\t<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css\" integrity=\"sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T\" crossorigin=\"anonymous\">\n")
    f.write(f"\t\t<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css\">\n")
    f.write(f"\t\t<script src=\"https://cdn.jsdelivr.net/npm/clipboard@2.0.10/dist/clipboard.min.js\"></script>\n")
    f.write(f"\t\t<script type=\"text/x-mathjax-config\">MathJax.Hub.Config({{tex2jax: {{inlineMath: [['$','$'], ['\\(','\\)']]}}}});</script>\n")
    f.write(f"\t\t<script type=\"text/javascript\" src=\"http://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>\n")
    f.write(f"\t</head>\n")
    f.write(f"\t<body>\n")

    f.write(f"\t\t<h1>Settings</h1>\n")
    f.write(f"\t\t<table class=\"table table-striped\">\n")
    f.write(f"\t\t<thead class=\"thead-dark\">\n")
    f.write(f"\t\t<tr><th scope=\"col\">Setting</th><th scope=\"col\">Value</th></tr>\n")
    f.write(f"\t\t</thead>")
    f.write(f"\t\t<tbody>")
    for key in settings:
        f.write(f"\t\t<tr><td>{key}</td><td>{settings[key]}</td></tr>\n") 
    f.write(f"\t\t</tbody>")  
    f.write(f"\t\t</table>\n")

    f.write(f"\t\t<h1>Exploration</h1>\n")
    f.write(f"\t\t<table class=\"table table-striped\">\n")
    f.write(f"\t\t<thead class=\"thead-dark\">\n")
    f.write(f"\t\t<tr><th scope=\"col\">id</th><th scope=\"col\">state</th><th scope=\"col\">lb_lemma</th><th scope=\"col\">lb_str</th><th scope=\"col\">ub_lemma</th><th scope=\"col\">ub_str</th><th scope=\"col\">plot</th><th scope=\"col\">lb_fn</th><th scope=\"col\">ub_fn</th></tr>\n")
    f.write(f"\t\t</thead>")
    f.write(f"\t\t<tbody>")
    for cell in table:
        if cell is not None:

            _plot_cell(settings, filename, cell)

            f.write("\t\t<tr>")
            f.write(
                f"<td>{str(int(cell.get_state()))}</td>" +
                f"<td>{str(cell.get_state())}</td>" +
                f"<td>{str(cell.get_lb_lemma())}</td>" +
                f"<td>${str(cell.get_lb_str())}$</td>" +
                f"<td>{str(cell.get_ub_lemma())}</td>" +
                f"<td>${str(cell.get_ub_str())}$</td>" +
                f"<td><img class=\"img-fluid\" src=\"{filename}-{int(cell.get_state())}.png\"></td>" +
                f"<td><input class=\"form-control\" id=\"lb-fn-{str(int(cell.get_state()))}\" type=\"text\" value=\"{html.escape(str(dill.dumps(cell.get_lb_fn())))}\"/><button type=\"button\" class=\"btn btn-light\" data-clipboard-target=\"#lb-fn-{str(int(cell.get_state()))}\"><i class=\"bi bi-clipboard\"></i></button></td>" +
                f"<td><input class=\"form-control\" id=\"ub-fn-{str(int(cell.get_state()))}\" type=\"text\" value=\"{html.escape(str(dill.dumps(cell.get_ub_fn())))}\"/><button type=\"button\" class=\"btn btn-light\" data-clipboard-target=\"#ub-fn-{str(int(cell.get_state()))}\"><i class=\"bi bi-clipboard\"></i></button></td>"
            )
            f.write("\t\t</tr>\n")
    f.write(f"\t\t</tbody>")
    f.write(f"\t\t</table>\n")

    f.write(f"\t\t<script>new ClipboardJS('.btn');</script>")
    f.write(f"\t</body>\n")
    f.write(f"</html>\n")

    f.close()

def _save_html_cards(settings, table: List[Cell]) -> None:
    """
    Save a `table` created under `settings` as a `.html` for ease of
    comprehension and visualization.
    """

    filename = datetime.now().strftime("%Y%m%d%H%M%S")

    os.mkdir(PATH_TO_HTML_DIR + filename + "/")
    f = open(PATH_TO_HTML_DIR + filename + "/" + filename + ".html", "w")

    f.write(f"<html>\n")
    f.write(f"\t<head>\n")
    f.write(f"\t\t<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css\" integrity=\"sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T\" crossorigin=\"anonymous\">\n")
    f.write(f"\t\t<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css\">\n")
    f.write(f"\t\t<script src=\"https://cdn.jsdelivr.net/npm/clipboard@2.0.10/dist/clipboard.min.js\"></script>\n")
    f.write(f"\t\t<script type=\"text/x-mathjax-config\">MathJax.Hub.Config({{tex2jax: {{inlineMath: [['$','$'], ['\\(','\\)']]}}}});</script>\n")
    f.write(f"\t\t<script type=\"text/javascript\" src=\"http://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>\n")
    f.write(f"\t</head>\n")
    f.write(f"\t<body>\n")

    f.write(f"\t\t<h1>Settings</h1>\n")
    f.write(f"\t\t<table class=\"table table-striped\">\n")
    f.write(f"\t\t<thead class=\"thead-dark\">\n")
    f.write(f"\t\t<tr><th scope=\"col\">Setting</th><th scope=\"col\">Value</th></tr>\n")
    f.write(f"\t\t</thead>")
    f.write(f"\t\t<tbody>")
    for key in settings:
        f.write(f"\t\t<tr><td>{key}</td><td>{settings[key]}</td></tr>\n") 
    f.write(f"\t\t</tbody>")  
    f.write(f"\t\t</table>\n")

    f.write(f"\t\t<h1>Exploration</h1>\n")
    f.write(f"\t\t<table class=\"table table-striped\">\n")
    f.write(f"\t\t<thead class=\"thead-dark\">\n")
    f.write(f"\t\t<tr><th scope=\"col\"></th></tr>\n")
    f.write(f"\t\t</thead>")
    f.write(f"\t\t<tbody>")
    for cell in table:
        if cell is not None:

            _plot_cell(settings, filename, cell)
            
            f.write(f"\t\t<tr><td>\n")
            f.write(f"\t\t<div class=\"container-fluid\">\n")
            f.write(f"\t\t\t<div class=\"row\">\n")
            f.write(f"\t\t\t\t<div class=\"col-md-12\">\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t{str(int(cell.get_state()))}\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"\t\t\t\t\t<h2>\n")
            f.write(f"\t\t\t\t\t\t{str(cell.get_state())}\n")
            f.write(f"\t\t\t\t\t</h2>\n")
            f.write(f"<hr />\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Lemmas used for lower bound:</b>&nbsp;{str(cell.get_lb_lemma())}\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Value of lower bound:</b>&nbsp;${str(cell.get_lb_str())}$\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"<hr />\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Lemmas used for upper bound:</b>&nbsp;{str(cell.get_ub_lemma())}\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Value of upper bound:</b>&nbsp;${str(cell.get_ub_str())}$\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"<hr />\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Serialized Python code for lower bound:</b><input class=\"form-control\" id=\"lb-fn-{str(int(cell.get_state()))}\" type=\"text\" value=\"{html.escape(str(dill.dumps(cell.get_lb_fn())))}\"/><button type=\"button\" class=\"btn btn-light\" data-clipboard-target=\"#lb-fn-{str(int(cell.get_state()))}\"><i class=\"bi bi-clipboard\"></i></button>\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"\t\t\t\t\t<p>\n")
            f.write(f"\t\t\t\t\t\t<b>Serialized Python code for upper bound:</b><input class=\"form-control\" id=\"ub-fn-{str(int(cell.get_state()))}\" type=\"text\" value=\"{html.escape(str(dill.dumps(cell.get_ub_fn())))}\"/><button type=\"button\" class=\"btn btn-light\" data-clipboard-target=\"#ub-fn-{str(int(cell.get_state()))}\"><i class=\"bi bi-clipboard\"></i></button>\n")
            f.write(f"\t\t\t\t\t</p>\n")
            f.write(f"<hr />\n")
            f.write(f"\t\t\t\t\t<img class=\"img-fluid\" src=\"{filename}-{int(cell.get_state())}.png\">\n")
            f.write(f"\t\t\t\t</div>\n")
            f.write(f"\t\t\t</div>\n")
            f.write(f"\t\t</div>\n")
            f.write(f"\t\t</td></tr>\n")

    f.write(f"\t\t</tbody>")
    f.write(f"\t\t</table>\n")

    f.write(f"\t\t<script>new ClipboardJS('.btn');</script>")
    f.write(f"\t</body>\n")
    f.write(f"</html>\n")

    f.close()

def _plot_cell(settings, filename: str, cell: Cell) -> None:
    """
    Plot the lower and upper bounds as a function of alpha for the state
    represented by `cell` which was created under `settings`. Save the
    plot so that it may be accessed by the `.html` file with `filename`.
    """

    if any(x is None for x in [cell.get_lb_lemma(), cell.get_lb_str(), cell.get_lb_fn(), cell.get_ub_lemma(), cell.get_ub_str(), cell.get_ub_fn()]):
        print(f"visualize._plot_cell: must fill in the lower and upper bounds to the cell before plotting")

    xs = np.linspace(settings["alpha-pos-lb"], settings["alpha-pos-ub"], 100)

    plt.plot([x for x in xs], [cell.get_lb_fn()(x) for x in xs], color="green")
    plt.plot([x for x in xs], [cell.get_ub_fn()(x) for x in xs], color="cyan")

    plt.tight_layout()

    plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{int(cell.get_state())}.png", transparent=True)

    plt.clf()