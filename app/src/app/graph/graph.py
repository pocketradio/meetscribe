from langgraph.graph import StateGraph, END
from app.graph.state import MeetingState
from app.crew import MeetscribeCrew

def crew_node(state : MeetingState) -> MeetingState:
    crew = MeetscribeCrew() # init crewai crew
    result = crew.crew().kickoff(inputs = {'transcript' : state['transcript']})
    
    # extract each output from results 
    state['summary'] = result.tasks_output[0].raw
    state['action_items'] = result.tasks_output[1].raw
    state['email'] = result.tasks_output[2].raw
    
    return state # since add_node has a return type of state

def human_review_node(state : MeetingState) -> MeetingState:
    print(f"\n=== EMAIL DRAFT ===\n{state['email']}\n") # shows email draft to the user
    approval = input("Approve? Enter a number : (1. Yes \n2. Edit draft \n3. Regenerate \n4. Stop): ")
    
    if approval == "1":
        state['decision'] = "send"
    elif approval == "2":
        new_draft = input("Enter updated email:\n")
        state["email"] = new_draft
        state['decision'] = "edit"
        
    elif approval == "3":
        state['decision'] = "regenerate"
    else:
        state['decision'] = "stop"
    
    return state
        
    
def handle_decision(state : MeetingState): # not a node since it doesn't perform any state change
    return state['decision']



# building the graph:
graph = StateGraph(MeetingState)
graph.add_node("crew", crew_node)
graph.add_node("review", human_review_node)


graph.set_entry_point("crew")
graph.add_edge("crew", "review")

graph.add_conditional_edges("review", handle_decision, {
    "send" : END,
    "edit" : "review",
    "regenerate" : "crew",
    "stop" : END
})

app = graph.compile()