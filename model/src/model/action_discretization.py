import torch

"""
:param pr_ltx: softmax of the action space for left top x coordinate
:param pr_tly: softmax of the action space for left top y coordinate
:param pr_brx: softmax of the action space for bottom right x coordinate
:param pr_bry: softmax of the action space for bottom right y coordinate
:param pr_ws: softmax of the action space for workspace number
:return: action indices suggested by the model
"""

def greedy_discretization(pr_ltx, pr_tly, pr_brx, pr_bry, pr_ws):
    """
    performs greedy discretization of the action space, simply choosing the action with the highest probability
    """
    tlx_action = torch.argmax(pr_ltx, dim=-1)
    tly_action = torch.argmax(pr_tly, dim=-1)
    brx_action = torch.argmax(pr_brx, dim=-1)
    bry_action = torch.argmax(pr_bry, dim=-1)
    ws_action = torch.argmax(pr_ws, dim=-1)
    return tlx_action, tly_action, brx_action, bry_action, ws_action

def stochastic_discretization(pr_ltx, pr_tly, pr_brx, pr_bry, pr_ws):
    """
    performs stochastic discretization of the action space, choosing randomized action based on the probabilities
    """
    batch_size, windows_number, _ = pr_ltx.shape
    flattened = (batch_size * windows_number, -1)
    pr_ltx = torch.multinomial(pr_ltx.view(flattened), 1).view(batch_size, windows_number)
    pr_tly = torch.multinomial(pr_tly.view(flattened), 1).view(batch_size, windows_number)
    pr_brx = torch.multinomial(pr_brx.view(flattened), 1).view(batch_size, windows_number)
    pr_bry = torch.multinomial(pr_bry.view(flattened), 1).view(batch_size, windows_number)
    pr_ws = torch.multinomial(pr_ws.view(flattened), 1).view(batch_size, windows_number)
    return pr_ltx, pr_tly, pr_brx, pr_bry, pr_ws

def epsilon_greedy_discretization(pr_ltx, pr_tly, pr_brx, pr_bry, pr_ws, epsilon : float = 0.1):
    """
    performs epsilon greedy discretization of the action space, choosing random action with probability epsilon,
    otherwise choosing the greedy action
    """
    greedy = greedy_discretization(pr_ltx, pr_tly, pr_brx, pr_bry, pr_ws)
    random_tlx = torch.randint(0, pr_ltx.shape[-1], size=pr_ltx.shape)
    random_tly = torch.randint(0, pr_tly.shape[-1], size=pr_tly.shape)
    random_brx = torch.randint(0, pr_brx.shape[-1], size=pr_brx.shape)
    random_bry = torch.randint(0, pr_bry.shape[-1], size=pr_bry.shape)
    random_ws = torch.randint(0, pr_ws.shape[-1], size=pr_ws.shape)
    tlx_action = torch.where(torch.rand(pr_ltx.shape) < epsilon, greedy[0], random_tlx)
    tly_action = torch.where(torch.rand(pr_tly.shape) < epsilon, greedy[1], random_tly)
    brx_action = torch.where(torch.rand(pr_brx.shape) < epsilon, greedy[2], random_brx)
    bry_action = torch.where(torch.rand(pr_bry.shape) < epsilon, greedy[3], random_bry)
    ws_action = torch.where(torch.rand(pr_ws.shape) < epsilon, greedy[4], random_ws)
    return tlx_action, tly_action, brx_action, bry_action, ws_action
