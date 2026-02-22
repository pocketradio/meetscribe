from langgraph.graph import StateGraph, END
from app.graph.state import MeetingState
from app.crew import MeetscribeCrew
from langgraph.checkpoint.memory import MemorySaver

def crew_node(state : MeetingState) -> MeetingState:
    crew = MeetscribeCrew() # init crewai crew
    result = crew.crew().kickoff(inputs = {'transcript' : state['transcript']})
    
    # extract each output from results 
    state['summary'] = result.tasks_output[0].raw
    state['action_items'] = result.tasks_output[1].raw
    state['email'] = result.tasks_output[2].raw
    
    return state # since add_node has a return type of state

def human_review_node(state : MeetingState) -> MeetingState:
    # pausing for human review through UI
    # stream() ends here and control returns to streamlit before continuing stream from there. 

    return state
        
    
def handle_decision(state : MeetingState): # not a node since it doesn't perform any state change
    
    return state.get("decision", "review")

    #interrupt will protect first run but "review" is kept as a defense. wont crash mostly.


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

checkpointer = MemorySaver()
app = graph.compile(
    checkpointer,
    interrupt_before=['review'] # ie. pause before every review node 
)
