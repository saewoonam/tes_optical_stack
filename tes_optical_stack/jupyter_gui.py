import ipywidgets as widgets
from ipywidgets import Button, HBox, VBox, Layout, Label
import lmfit
import numpy as np
import functools


def layers2t(layers):
    t = []
    for key in layers.keys():
        t.append(layers[key].value)
    return t


def build_gui_layer_v2(name, guess, nk):
    cb = widgets.Checkbox(
            value=False,
            #description=f'vary:',
            disabled=False,
            indent=False,
            layout=Layout(width='40px')
            )

    #label = widgets.Label(f'{name}')
    label = widgets.Dropdown(
      options=nk.keys(),
      value=nk[name].name,
      description='',
      disabled=False,
    )
    if guess==np.inf:
        guess_widget = widgets.Label('inf', layout=Layout(width='150px'))
        cb.disabled=True
    else:
        guess_widget = widgets.BoundedFloatText(
            value=guess,
            min=1,
            max=2000,
            #step=0.1,
            #description=f'{name}:',
            disabled=False,
            layout=Layout(width='150px')
        )
    return cb, label, guess_widget

def build_gui_v2(stack_description, init_guess, nk):
    vary_gui = [Label('vary')]
    labels_gui = [Label('material')]
    guess_gui = [Label('initial guess')]
    delete_gui = [Label('remove')]
    up_gui = [Label('move')]
    down_gui = [Label('')]
    insert_up_gui = [Label('insert')]
    insert_down_gui = [Label('')]
    idx = 0  # 1 skip incoming index
    while idx < len(stack_description): #-1:  # skip output index
        name = stack_description[idx]
        guess = init_guess[idx]
        cb, label, guess_widget = build_gui_layer_v2(name, guess, nk)

        delete_button = widgets.Button(icon='fa-times', layout=Layout(width='40px'))
        up_button = widgets.Button(icon='arrow-up', layout=Layout(width='40px'))
        down_button = widgets.Button(icon='arrow-down', layout=Layout(width='40px'))
        insert_up_button = widgets.Button(icon='chevron-up', layout=Layout(width='40px'))
        insert_down_button = widgets.Button(icon='chevron-down', layout=Layout(width='40px'))
        if idx==0:
            delete_button.disabled = True
            insert_up_button.disabled = True
        if idx == (len(stack_description)-1):
            delete_button.disabled = True
            insert_down_button.disabled = True
        #print(name, guess)
        idx += 1
        vary_gui.append(cb)
        labels_gui.append(label)
        #labels_gui.append(HBox([label, guess_widget])
        guess_gui.append(guess_widget)
        delete_gui.append(delete_button)
        up_gui.append(up_button)
        down_gui.append(down_button)
        insert_up_gui.append(insert_up_button)
        insert_down_gui.append(insert_down_button)
    label_box = VBox(labels_gui)
    guess_box = VBox(guess_gui)
    vary_box = VBox(vary_gui)
    delete_box = VBox(delete_gui)
    up_box = VBox(up_gui)
    down_box = VBox(down_gui)
    insert_up_box = VBox(insert_up_gui)
    insert_down_box = VBox(insert_down_gui)

    stack_gui = HBox([label_box, guess_box, vary_box, up_box, down_box,
                      delete_box, insert_up_box, insert_down_box])
    # Add actions on button clicks
    #add on_delete to button
    def on_delete(b):
        # find index to delete
        delete_idx = stack_gui.children[-3].children.index(b)
        #print('index = ', delete_idx)
        #print(len(stack_gui.children))
        for idx in range(len(stack_gui.children)):
            #print(stack_gui.children[idx].children[delete_idx])
            vbox_kids = list(stack_gui.children[idx].children)
            vbox_kids.pop(delete_idx)
            stack_gui.children[idx].children = tuple(vbox_kids)
    #delete_button.on_click(on_delete)
    for child in stack_gui.children[-3].children[1:]:
        child.on_click(on_delete)
        
    def on_up(b):
        up_idx = stack_gui.children[-5].children.index(b)
        for idx in range(len(stack_gui.children)):
            vbox_kids = list(stack_gui.children[idx].children)
            if up_idx > 1:
                vbox_kids[up_idx-1], vbox_kids[up_idx] = vbox_kids[up_idx], vbox_kids[up_idx-1]
            stack_gui.children[idx].children = tuple(vbox_kids)
    #up_button.on_click(on_up)
    for child in stack_gui.children[-5].children[1:]:
        child.on_click(on_up)
    def on_down(b):
        down_idx = stack_gui.children[-4].children.index(b)
        #print('down_idx', down_idx)
        for idx in range(len(stack_gui.children)):
            vbox_kids = list(stack_gui.children[idx].children)
            if down_idx < (len(vbox_kids)-1):
                vbox_kids[down_idx+1], vbox_kids[down_idx] = vbox_kids[down_idx], vbox_kids[down_idx+1]
            stack_gui.children[idx].children = tuple(vbox_kids)
    #down_button.on_click(on_down)
    for child in stack_gui.children[-4].children[1:]:
        child.on_click(on_down)

    def on_insert(b, offset=0):
        up_idx = stack_gui.children[-2+offset].children.index(b)
        # create elements for a new layer
        cb, label, guess_widget = build_gui_layer_v2('air', 1, nk)
        delete_button = widgets.Button(icon='fa-times', layout=Layout(width='40px'))
        up_button = widgets.Button(icon='arrow-up', layout=Layout(width='40px'))
        down_button = widgets.Button(icon='arrow-down', layout=Layout(width='40px'))
        insert_up_button = widgets.Button(icon='chevron-up', layout=Layout(width='40px'))
        insert_down_button = widgets.Button(icon='chevron-down', layout=Layout(width='40px'))

        layer_elements = [label, guess_widget, cb, up_button, down_button,
                          delete_button, insert_up_button, insert_down_button]
        for idx in range(len(stack_gui.children)):
            vbox_kids = list(stack_gui.children[idx].children)
            vbox_kids.insert(up_idx+offset, layer_elements[idx])
            stack_gui.children[idx].children = tuple(vbox_kids)
        delete_button.on_click(on_delete)
        up_button.on_click(on_up)
        down_button.on_click(on_down)
        insert_up_button.on_click(on_insert_up)
        insert_down_button.on_click(on_insert_down)

    #insert_up_button.on_click(on_insert_up)
    on_insert_up = functools.partial(on_insert, offset=0)
    on_insert_down = functools.partial(on_insert, offset=1)
    for child in stack_gui.children[-2].children[1:]:
        child.on_click(on_insert)
    for child in stack_gui.children[-1].children[1:]:
        child.on_click(on_insert_down)
    return stack_gui

def gui2layers_v2(stack_gui, offset=1):
    layers = lmfit.Parameters()
    layer_number = 0

    #name = 'air'
    #p = lmfit.Parameter(f'layer{layer_number}', value=np.inf, min=1, max=np.inf, user_data={'name':name})
    #p.vary = False
    #layers.add(p)
    idx = offset 
    #idx=0
    while idx < len(stack_gui.children[0].children):
        layer_number += 1
        name = stack_gui.children[0].children[idx].value
        t = stack_gui.children[1].children[idx].value
        if t=='inf':
            t = np.inf
        vary = stack_gui.children[2].children[idx].value
        print(name, t, vary)
        if 'W' in name:
            p = lmfit.Parameter(f'layer{layer_number}', value=t, min=1, max=2000, user_data={'name':name})
        else:
            if t==np.inf:
                p = lmfit.Parameter(f'layer{layer_number}', value=np.inf, min=1, max=np.inf, user_data={'name':name})
            else:
                p = lmfit.Parameter(f'layer{layer_number}', value=t, min=0, max=2000, user_data={'name':name})
        p.vary = vary
        layers.add(p)
        idx += 1
        # print(name, t, vary)

    #name = 'air'
    #p = lmfit.Parameter(f'layer{layer_number+1}', value=np.inf, min=1, max=np.inf, user_data={'name':name})
    #p.vary = False
    #layers.add(p)
    return layers
