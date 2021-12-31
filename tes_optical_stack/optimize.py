import ipywidgets as widgets
from ipywidgets import Button, HBox, VBox, Layout
import lmfit
import numpy as np


def layers2t(layers):
    t = []
    for key in layers.keys():
        t.append(layers[key].value)
    return t


def build_gui(stack_description, init_guess):
    vary_gui = []
    labels_gui = []
    guess_gui = []
    idx = 1  # skip incoming index
    while idx < len(stack_description)-1:  # skip output index
        name = stack_description[idx]
        guess = init_guess[idx]
        cb = widgets.Checkbox(
                value=False,
                description=f'vary:',
                disabled=False,
                indent=False
                )

        label = widgets.Label(f'{name}')
        guess_widget = widgets.BoundedFloatText(
                value=guess,
                min=1,
                #max=np.inf,
                #step=0.1,
                #description=f'{name}:',
                disabled=False,
                layout=Layout(width='150px')
                )

        #print(name, guess)
        idx += 1
        vary_gui.append(cb)
        labels_gui.append(label)
        #labels_gui.append(HBox([label, guess_widget])
        guess_gui.append(guess_widget)
    label_box = VBox(labels_gui)
    guess_box = VBox(guess_gui)
    vary_box = VBox(vary_gui)
    stack_gui = HBox([label_box, guess_box, vary_box])
    return stack_gui

def gui2layers(stack_gui):
    layers = lmfit.Parameters()
    idx = 0

    name = 'air'
    p = lmfit.Parameter(f'layer{idx}', value=np.inf, min=1, max=np.inf, user_data={'name':name})
    p.vary = False
    layers.add(p)

    while idx < len(stack_gui.children[0].children):
        idx += 1
        name = stack_gui.children[0].children[idx-1].value
        t = stack_gui.children[1].children[idx-1].value
        vary = stack_gui.children[2].children[idx-1].value
        if 'W' in name:
            p = lmfit.Parameter(f'layer{idx}', value=t, min=1, max=1000, user_data={'name':name})
        else:
            p = lmfit.Parameter(f'layer{idx}', value=t, min=0, max=1000, user_data={'name':name})
        p.vary = vary
        layers.add(p)
        # print(name, t, vary)

    name = 'air'
    p = lmfit.Parameter(f'layer{idx+1}', value=np.inf, min=1, max=np.inf, user_data={'name':name})
    p.vary = False
    layers.add(p)
    return layers
