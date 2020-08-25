from collections import deque, namedtuple
import random as rnd
import subprocess

import numpy as np
from clyngor import ASP

from utils import get_overlap, get_distance

AnswerSet = namedtuple('AS', ['r', 'p', 'a']) # r for raw, p for parsed, a for arity
parse_args = lambda x: list(list(ASP(x+'.').parse_args)[0])[0]
sample_vars = ["X", "Y", "Z"]
macro_actions = {
    "explore":3,
    "interact":1,
    # "rotate":0
}
valid_observables = {
    'present',
    'visible',
    'on',
    'adjacent',
    'goal',
    'goal1',
    'wall',
    'platform'
}


class Grounder:
    def __init__(self):
        pass
    # @staticmethod
    # def in_front(macro_step,state):
    #     in_front = ""
    #     for bbox, _, _, _id in state['obj']:
    #         for bbox1, _, _, _id1 in state['obj']:
    #             dist = get_distance(bbox, bbox1)
    #             if (_id1!=_id)&(dist<0.02):
    #                 in_front += f"adjacent({_id},{_id1}, {macro_step}).\n"
    #     return in_front
    @staticmethod
    def adjacent(macro_step,state):
        adjacent = ""
        for bbox, _, _, _id in state['obj']:
            for bbox1, _, _, _id1 in state['obj']:
                dist = get_distance(bbox, bbox1)
                if (_id1!=_id)&(dist<0.02):
                    adjacent += f"adjacent({_id},{_id1}, {macro_step}).\n"
        return adjacent
    @staticmethod
    def timestep(macro_step,_):
        timestep = f"timestep({macro_step}).\n"
        return timestep
    @staticmethod
    def on(macro_step,state):
        on = ""
        bottom_rect = [0, 0.75, 1, 0.25]
        for bbox, _, _, _id in state['obj']:
            if get_overlap(bbox, bottom_rect)>0.5:
                on += f"on(agent,{_id},{macro_step}).\n"
        return on

    @staticmethod
    def visible(macro_step,state):
        visible = ""
        for _, obj_type, _occ_area, _id in state['obj']:
            visible += f"visible({_id},{_occ_area},{macro_step}).\n"
            if obj_type!="goal":
                visible +=f"{obj_type}({_id}).\n"
        return visible
    @staticmethod
    def goal_visible(_,state):
        try:
            gg_id = next(i[3] for i in state['obj'] if i[1] in ['goal', 'goal1'])
        except StopIteration:
            gg_id = 42
        return f"goal({gg_id}).\n"
    def run(self, macro_step, state):
        res = ""
        for k,v in vars(Grounder).items():
            if isinstance(v, staticmethod):
                res+= getattr(self, k)(macro_step,state)
        return res

class Ilasp:
    def __init__(self):
        # Examples are [int:weight, string:example]
        self.memory_len = 30
        self.examples = deque(maxlen=self.memory_len)
        self.macro_actions_learned = []

    def create_modeh(self):
        res = ""
        for name, num_preds in macro_actions.items():
            if name in self.macro_actions_learned:
                continue
            if num_preds:
                variables = "("
                for i in range(num_preds):
                    variables+=f"var({sample_vars[i]}),"
                variables = variables[:-1] + ')' # get rid of last comma
            else:
                variables = ""
            res += f"#modeh(1, initiate({name}{variables},var(T))).\n"

        return res + "#maxv(4).\n"

    def create_modeb(self):
        return """
        #modeb(1, goal(var(X))).
        #modeb(1, visible(var(X), var(Z), var(T))).
        #modeb(1, occludes(var(X),var(Y), var(T))).\n"""
    def update_examples(self, observables, actions, success):
        # gamma = 1
        heuristic = max(5-len(actions),1)

        observables = '\n'.join(observables)
        actions = ','.join(actions)

        idf = len(self.examples)
        if success:
            example = f"#pos(a{idf}@{heuristic},\n{{{actions}}},\n{{}},\n{{{observables}}}).\n"
        else:
            example = f"#pos(a{idf}@{heuristic},\n{{}},\n{{{actions}}},\n{{{observables}}}).\n"
        self.examples.append([success, example])

        success_num = sum([i[0] for i in self.examples])
        # print(success_num)
        if success_num==self.memory_len:
            ratio = self.memory_len-1
            mult = 1
        elif not success_num:
            mult = self.memory_len-1
            ratio = 1
        else:
            ratio = success_num/(self.memory_len-success_num)
            mult = 10 if ratio>1 else 100
            ratio = int(ratio*mult)
        if len(self.examples) == self.memory_len:
            for c, (suc, eg) in enumerate(self.examples):
                weight = 1 #mult if suc else ratio
                a_idx = eg.index('a')+1
                c_idx = eg.index(",")
                updated_eg = eg[:a_idx] + str(c) + "@" + str(weight) +  eg[c_idx:]
                self.examples[c] = [suc, updated_eg]            
            # for c, eg in enumerate(self.examples):
            #     at_index = eg[1].index('@') # first comma
            #     updated_eg = eg[1][:6] + f"{c}" + eg[1][at_index:]
            #     self.examples[c] = [c, updated_eg]

    def write_examples(self):
        res = ""
        for eg in self.examples:
            res+= eg[1] + '\n'
        return res
    def run(self, lp):        
        # Create text file with lp
        with open("tmp.lp", "w") as text_file:
            text_file.write(lp+self.create_modeh()+self.create_modeb() + self.write_examples())
        # Start bash process that runs ilasp learning
        bashCommand = "ilasp --version=2i tmp.lp -q"
        process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        if error:
            raise Exception(f"ILASP error: {erorr.decode('utf-8')}")
        
        # Return new lp with learned rules
        if bool(output): #learned rules
            output = output.decode("utf-8")

            if output:
                print(f"NEW RULES LEARNED: {output}")
            if output=="UNSATISFIABLE\n":
                return False
            for ma in macro_actions:
                if ma in output:
                    self.macro_actions_learned.append(ma)
            return output
        print("NO RULES LEARNED")
        return False # No learned rules, will choose random macro
        
        
class Clingo:
    def __init__(self):
        self.macro_actions_learned = []

    def random_action_grounder(self, macro_step, ground_observables):
        lp = f"""
            {ground_observables}
            present(X,T):-goal(X), timestep(T).
            present(X,T):- visible(X, _, T).
            initiate(explore(X,Y,O),T):- visible(X, O, T), present(Y,T), X!=Y.
            initiate(interact(X),T):-visible(X,_,T).
            initiate(rotate,{macro_step})."""
        res = self.asp(lp)
        filtered_mas = [i for i in res.r[0] if (
            'initiate' in i)&(not any(j in i for j in self.macro_actions_learned))]
        rand_action = rnd.choice(filtered_mas)
        # print([i for i in res.r[0] if 'initiate' in i])
        return [[rand_action]]

    @staticmethod
    def asp(lp):
        as1 = list(ASP(lp).atoms_as_string)
        as2 = list(ASP(lp).parse_args)

        return AnswerSet(r=as1, p=as2, a=len(as1))


    def macro_processing(self, answer_set):
        # Look for initiate
        res = {
            'initiate':[],
            'check':[],
            'raw':[]
        }
        if not isinstance(answer_set, list):
            answer_set = answer_set.r
        if len(answer_set)>1:
            print("More than 1 answer set so stopping at first initiate")
            print(answer_set)
            _break = True
        else:
            _break = False

        for ans_set in answer_set:
            for literal in ans_set:
                if 'initiate' in literal:
                    # From initiate(action(args),ts), select action(args)
                    res['initiate'].append(parse_args(literal)[1][0])
                    res['raw'].append(literal)
                    if _break:
                        break


        # No action returned
        if not res['initiate']:
            print("NO ACTION")
            return False

        # if two actions are returned from program then use random action.
        if len(res['initiate'])>1:
            print("More than one action")
            # print(res['initiate'])
            res['raw'] = "–".join(res['initiate'])
            res['initiate'] = random.choice(res['initiate'])
            # return False

        # Add checks for chosen action
        checks = list(ASP(f"""            
            {res['raw'][0]}.
            check(visible, Y):- initiate(explore(X,Y,Z),T).
            check(time, 250):- initiate(explore(X,Y,Z),T).
            check(time, 100):- initiate(interact(X),T).
            check(time, 50):- initiate(rotate,T).""").atoms_as_string)
        checks = checks[0]
        checks = [parse_args(i)[1] for i in list(checks) if 'check' in i]
        res['check'] = checks
        # print(res)
        return res

    def run(self, macro_step, lp, random=False):
        # Just ground macro actions based on observables
        if random:
            res = self.random_action_grounder(macro_step, lp)
        else: # Run full lp
            # print(lp)
            res = self.asp(lp)
            # print(res)
            # print(lp)
            # print(res)
                
        return self.macro_processing(res)

class Logic:
    def __init__(self):
        self.grounder = Grounder()
        self.ilasp = Ilasp()
        self.clingo = Clingo()
        self.e = 1
        self.e_discount = 8e-3
        self.learned_lp = ""

    def macro_kb(self):
        """This is what we want to learn."""
        return """
            0{initiate(explore(X,Y,Z),T)}1:- visible(X,Z,T), occludes(X,Y,T).
            initiate(interact(X),T):- visible(X, _,T), goal(X).
            initiate(rotate,T):- not visible(T), timestep(T)."""
    def main_lp(self):
        return f"""
        present(X,T):-goal(X), timestep(T).
        % Observables rules
        present(X,T):- visible(X, _, T).
        visible(T):- visible(X, _, T).
        not_occluding(X, T):-on(agent, X, T).
        separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
        occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).
        % Observables - > actions: this is what we need to learn
        initiate(rotate,T):- not visible(T), timestep(T).
"""

    def test_lp(self):
        return """
        present(X,T):- visible(X, _, T).
        visible(T):- visible(X, _, T).
        present(X,T):-goal(X), timestep(T).
        not_occluding(X, T):-on(agent, X, T).
        separator(Y, T):-on(agent, X, T), adjacent(X, Y, T), platform(X).
        occludes(X,Y,T) :- present(Y, T), visible(X, _, T), not visible(Y, _, T), not separator(X, T), not not_occluding(X, T).

        :- initiate(explore(X1,Y,_), T), initiate(explore(X2,Y,_), T), X1 != X2.
        :~initiate(explore(X,Y,Z),T).[-Z@1,Z]
        0{initiate(explore(X,Y,Z),T)}1:- visible(X,Z,T), occludes(X,Y,T).
        initiate(interact(X),T):- visible(X, _,T), goal(X).
        initiate(rotate,T):- not visible(T), timestep(T).

        check(visible(Y),T):- initiate(explore(X,Y,Z),T).
        check(time, 150):- initiate(explore(X,Y,Z),T).
        check(time, 150):- initiate(interact(X),T).
        check(time, 50):- initiate(rotate,T)."""

    def e_greedy(self):
        # Don't start egreedy until there's at least one positive example with inclusion
        res = np.random.choice(['ilasp', 'random'], 1, p=[1-self.e, self.e])
        self.e = max(0.05, self.e - self.e_discount)
        print(f"E greedy = {self.e} and choice= {res}")
        return res


    def update_learned_lp(self, macro_step):
        rules_learned = self.ilasp.run(self.learned_lp)
        if rules_learned:
            self.learned_lp += rules_learned
            # Sync two lists
            self.clingo.macro_actions_learned = self.ilasp.macro_actions_learned

    def update_examples(self, observables, actions, success):
        self.ilasp.update_examples(observables, actions, success)

    def run(self, macro_step, state, choice='random'):
        # Ground state into high level observable predicates
        observables = self.grounder.run(macro_step, state)

        if choice!="test":      
            if not self.learned_lp:
                self.learned_lp = self.main_lp()


            if choice == 'ilasp':
                if self.learned_lp:
                    action = self.clingo.run(macro_step, self.learned_lp +observables, random=False)
                else:
                    action = self.clingo.run(macro_step, observables, random=True)

            elif choice == 'random':
                action = self.clingo.run(macro_step, observables, random=True)
            else:
                raise Exception("Modality not recognised")
            
            if not action:
                # print("No action choosing randomly")
                action = self.clingo.run(macro_step, observables, random=True)
            return action, observables
        # print(self.test_lp()+observables)
        action = self.clingo.run(
            macro_step, self.test_lp() + observables, random=False)
        if not action:
            action = self.clingo.run(macro_step, observables, random=True)
        return action
