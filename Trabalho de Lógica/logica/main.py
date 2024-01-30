import sys
from instance_manager.satplan_instance import *
from pysat.solvers import Glucose3
import time
from memory_profiler import profile
import psutil

def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~","")
    return f"~{level}_{pure_atom}" if literal[0] == "~" else f"{level}_{pure_atom}"

def create_literals_for_level_from_list(level, literals):
    return [create_literal_for_level(level, literal) for literal in literals]

def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state

def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

def printUsoDeMemoria():
    process = psutil.Process()
    mem_usage = process.memory_info().rss / (1024 ** 2)  # em megabytes
    print(f"Uso de Memória: {mem_usage:.2f} MB")

@profile
def main():
    satPlanInstance = SatPlanInstance(sys.argv[1])
    instanceMapper  = SatPlanInstanceMapper()
    instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())
    gluc = Glucose3()
    
    
    n_level = sys.maxsize   #MAIOR NUMERO INTEIRO, QUE REPRESENTA O N(INFINITO)
    for i in range(1, n_level): #UM LAÇOI DE RPETIÇÃO QUE VAI DO NIVEL 1 AO INFINITO
        a = create_literals_for_level_from_list(i, satPlanInstance.get_actions())
        # print(a)
        instanceMapper.add_list_of_literals_to_mapping(a)
        
        # print(actions_list)

        for actions in satPlanInstance.get_actions():
            pre_condition = create_literals_for_level_from_list(i, satPlanInstance.get_action_preconditions(actions))
            # CRIA OS LITERAIS DAS PRE CONDIÇÕES
            acoes_level= create_literal_for_level(i, actions)
            #CRIA OS LITERAIS DAS AÇÕES POR LEVEL 
            instanceMapper.add_list_of_literals_to_mapping(pre_condition)
            #instanceMapper.add_list_of_literals_to_mapping(pre_condition)
            for pre in pre_condition:
                mapped_condition = instanceMapper.get_literal_from_mapping(pre)   #MAPEIA AS PRE-CONDIÇÕES E MANDA PARA O SOLVER
                gluc.add_clause([-instanceMapper.get_literal_from_mapping(acoes_level), mapped_condition])
            
            pos_condition = create_literals_for_level_from_list(i+1, satPlanInstance.get_action_posconditions(actions))
            instanceMapper.add_list_of_literals_to_mapping(pos_condition)
            for pos in pos_condition:   #MAPEIA AS POS-CONDIÇÕES E MANDA PRO SOLVER
                mapped_condition2 = instanceMapper.get_literal_from_mapping(pos)
                gluc.add_clause([-instanceMapper.get_literal_from_mapping(acoes_level), mapped_condition2])  
            
            
        # print(f'Inicial: {satPlanInstance.get_initial_state()}')
        initials_states = create_state_from_literals(satPlanInstance.get_initial_state(), satPlanInstance.get_state_atoms())
        estado_inicial = create_literals_for_level_from_list(1, initials_states)
        instanceMapper.add_list_of_literals_to_mapping(estado_inicial)
        for estado in instanceMapper.get_list_of_literals_from_mapping(estado_inicial):
            gluc.add_clause([estado])
        
        # print(f'Final: {satPlanInstance.get_final_state()}')
        estado_final = create_literals_for_level_from_list(i, satPlanInstance.get_final_state())
        # print(estado_final)
        instanceMapper.add_list_of_literals_to_mapping(estado_final)
        
        for estado in instanceMapper.get_list_of_literals_from_mapping(estado_final):
            gluc.add_clause([estado])
        
        for j in range(1,i):
            for acao in satPlanInstance.get_actions():
                poscondition = satPlanInstance.get_action_posconditions(acao) #pos condiçoes para cada ação
                state= satPlanInstance.get_state_atoms()
                for estado in state:
                    if estado not in poscondition:
                        # AQUI MAPEIA OS LITERAIS POR NIVEL
                        level_estado = create_literal_for_level(j, estado)
                        level_acao = create_literal_for_level(j, acao)
                        level_prox_estado = create_literal_for_level(j + 1, estado)

                        # ADICIONA ELES AO SOLVER(estado atual true,proximo false)
                        gluc.add_clause([instanceMapper.get_literal_from_mapping(level_estado), -instanceMapper.get_literal_from_mapping(level_acao), -instanceMapper.get_literal_from_mapping(level_prox_estado)])
        for j in range(1, i): # Adiciona cláusulas para ações em cada nível
            acoesLevel = create_literals_for_level_from_list(j, satPlanInstance.get_actions())
            acoesMapeadas = instanceMapper.get_list_of_literals_from_mapping(acoesLevel)
            gluc.add_clause(acoesMapeadas)#ao menos uma ação escolhida
        
        
        gluc.solve()
        if gluc.get_model() != None:            #AQUI SE RESOLVIDO, PRINTA A RESOLUÇÃO
            print(f'NV{i}-resolvido')
            print('\n############ Resolução para o problema ############\n')
            for j in list(gluc.get_model()):
                if j > 0:

                    print(instanceMapper.get_literal_from_mapping_reverse(j))
            break
        else:
            print(f'NV{i}-não resolvido')
            gluc.delete()
            gluc = Glucose3()
 


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)       

    comecou = time.time()
    
    print('\nTrabalho realizado pelos alunos:\nPEDRO HENRIQUE DE ALMEIDA E PADUA\nJOAO VICTOR GOMES DOS SANTOS\n')
    
    main()

    acabou = time.time()
    tempoGasto = acabou - comecou
    print(f"\nTempo gasto pelo algoritimo: {tempoGasto} segundos ou {tempoGasto/60} minutos\n")
    printUsoDeMemoria()
    