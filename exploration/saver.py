from datetime import datetime
import dill
from jinja2 import Environment, FileSystemLoader, select_autoescape
import matplotlib.pyplot as plt
import numpy as np
import os
from symbols import *
import sympy as sp
import sys
import time

from bound import *
from commitment import *
from settings.setting import Setting
from state import State
from state_details import StateDetails
from state_utils import pretty_state_str

BOOTSTRAP_PRIMARY = "#007bff"
BOOTSTRAP_SUCCESS = "#28a745"

PATH_TO_OBJ_DIR = "temp/obj/"
PATH_TO_HTML_DIR = "temp/html/"

POINTS_SAMPLED = 100

plt.rcParams["figure.figsize"] = [7, 3]

env = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape()
)
template = env.get_template("template.html")
template.globals.update({
    "bound_isinstance": bound_isinstance,
    "hash": State.__hash__,
    "ActionBound": ActionBound,
    "ActionLowerBound": ActionLowerBound,
    "ActionUpperBound": ActionUpperBound,
    "CommitmentLowerBound": CommitmentLowerBound,
    "LemmaLowerBound": LemmaLowerBound,
    "LemmaUpperBound": LemmaUpperBound,
    "latex": sp.latex,
    "commitment_str": commitment_str,
    "pretty_state_str": pretty_state_str,
})

def save(settings: Setting, lut: dict[State, StateDetails]) -> None:
    """
    Save a `lut` created under `settings` according to the option
    selected in `settings`.
    """
    if settings["save_as"] == "serialized":
        _save_serialized(settings, lut)
    elif settings["save_as"] == "html":
        _save_html(settings, lut)
    else:
        print(f"saver.save: didn't recognize visualization settings {settings['save_as']}")
        sys.exit(1)

def _save_serialized(settings: Setting, lut: dict[State, StateDetails]) -> None:
    """
    Save a `lut` created under `settings` as a serialized Python
    object for future use.
    """
    f = open(PATH_TO_OBJ_DIR + datetime.now().strftime("%Y%m%d%H%M%S") + ".obj", "w")
    f.write(dill.dumps((settings, lut)))

def _save_html(settings: Setting, lut: dict[State, StateDetails]) -> None:
    """
    Save a `lut` created under `settings` as an `.html` table for
    ease of comprehension and visualization.
    """
    filename = datetime.now().strftime("%Y%m%d%H%M%S")

    os.mkdir(PATH_TO_HTML_DIR + filename + "/")
    f = open(PATH_TO_HTML_DIR + filename + "/" + filename + ".html", "w")

    start = time.time()
    x = 0

    for state in lut:
        x += _plot_state_details(settings, filename, lut[state])

    print(f"Made {x} plots in {int(time.time() - start)} seconds.")

    start = time.time()

    f.write(template.render(settings=settings, lut=lut, filename=filename))
    print(f"Rendered template in {int(time.time() - start)} seconds.")

def _plot_state_details(settings: Setting, filename: str, state_details: StateDetails) -> int:
    """
    Plot the lower and upper bounds as a function of alpha for the state
    represented by `state_details` which was created under `settings`. Save
    the plot so that it may be accessed by the `.html` file with `filename`.
    """
    n = 0

    xs = np.linspace(settings["alpha_pos_lower_bound"], settings["alpha_pos_upper_bound"], POINTS_SAMPLED)

    action_bounds = state_details.get_action_bounds()

    for i in range(len(action_bounds)):
        bound = action_bounds[i]

        lower_bound_fn = sp.lambdify(alpha, bound["immediate_reward"] + bound["lower_bound"], 'numpy')
        upper_bound_fn = sp.lambdify(alpha, bound["immediate_reward"] + bound["upper_bound"], 'numpy')

        plt.plot(xs, [lower_bound_fn(x) for x in xs], color=BOOTSTRAP_SUCCESS)
        plt.plot(xs, [upper_bound_fn(x) for x in xs], color=BOOTSTRAP_PRIMARY)

        plt.tight_layout()
        plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-action-{i}.png", transparent=True)
        n += 1
        plt.clf()

    commitment_bounds = state_details.get_commitment_bounds()
    
    for i in range(len(commitment_bounds)):
        bound = commitment_bounds[i]

        lower_bound_fn = sp.lambdify(alpha, bound["lower_bound"], 'numpy')

        plt.plot(xs, [lower_bound_fn(x) for x in xs], color=BOOTSTRAP_SUCCESS)

        plt.tight_layout()
        plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-commitment-{i}.png", transparent=True)
        n += 1
        plt.clf()

    lemma_bounds = state_details.get_lemma_bounds()
    
    for i in range(len(lemma_bounds)):
        bound = lemma_bounds[i]

        if bound_isinstance(bound, LemmaLowerBound):
            lower_bound_fn = sp.lambdify(alpha, bound["lower_bound"], 'numpy')

            plt.plot(xs, [lower_bound_fn(x) for x in xs], color=BOOTSTRAP_SUCCESS)

        else: # bound_isinstance(bound, LemmaUpperBound):
            upper_bound_fn = sp.lambdify(alpha, bound["upper_bound"], 'numpy')

            plt.plot(xs, [upper_bound_fn(x) for x in xs], color=BOOTSTRAP_PRIMARY)

        plt.tight_layout()
        plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-lemma-{i}.png", transparent=True)
        n += 1
        plt.clf()

    lower_bound_fn = sp.lambdify(alpha, (state_details.get_best_lower_bound()["immediate_reward"] if bound_isinstance(state_details.get_best_lower_bound(), ActionLowerBound) else sp.Integer(0)) + state_details.get_best_lower_bound()["lower_bound"], 'numpy')
    upper_bound_fn = sp.lambdify(alpha, (state_details.get_best_upper_bound()["immediate_reward"] if bound_isinstance(state_details.get_best_upper_bound(), ActionUpperBound) else sp.Integer(0)) + state_details.get_best_upper_bound()["upper_bound"], 'numpy')

    plt.plot(xs, [lower_bound_fn(x) for x in xs], color=BOOTSTRAP_SUCCESS)
    plt.tight_layout()
    plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-best-lower-bound.png", transparent=True)
    n += 1
    plt.clf()

    plt.plot(xs, [upper_bound_fn(x) for x in xs], color=BOOTSTRAP_PRIMARY)
    plt.tight_layout()
    plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-best-upper-bound.png", transparent=True)
    n += 1
    plt.clf()

    plt.plot(xs, [lower_bound_fn(x) for x in xs], color=BOOTSTRAP_SUCCESS)
    plt.plot(xs, [upper_bound_fn(x) for x in xs], color=BOOTSTRAP_PRIMARY)
    plt.tight_layout()
    plt.savefig(PATH_TO_HTML_DIR + f"{filename}/{filename}-{hash(state_details.get_state())}-best-bounds.png", transparent=True)
    n += 1
    plt.clf()

    return n