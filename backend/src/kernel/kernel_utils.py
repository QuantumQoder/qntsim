"""Definition of EventList class.
This module defines the EventList class, used by the timeline to order and execute events.
EventList is implemented as a min heap ordered by simulation time.
"""

from typing import List

from fibheap import Fheap

from .event import Event


class EventList(Fheap):
    """Class of event list.
    This class is implemented as a min-heap. The event with the lowest time and priority is placed at the top of fibonacci heap.
    
    Attributes:
        data (Fheap()): fibonacci heap storing events as nodes (where node.key = event).
        nodesl(List[Node(event)]):list of all nodes .
    """
    def __init__(self) -> None:
        Fheap.__init__(self)
        self.events: List["Event"] = []

    def __len__(self) -> int:
        return len(self.events)

    def __repr__(self) -> str:
        return f"EventList(num_events = {len(self)})\n\t" + "\n\t".join(str(event) for event in self.events)

    def __iter__(self) -> "Event":
        while not self.is_empty():
            yield self.pop()

    def push(self, event: "Event") -> None:
        """Method to insert the event into heap ,maintaing min-heap structure.
        The event is converted to heap node , appended to nodesl and inserted into heap.
        """
        self.insert(event)
        self.events.append(event)

    def pop(self) -> "Event":
        """Method to extract minium node (i.e, event with min time )
        """
        return self.extract_min()

    def is_empty(self) -> bool:
        return self.num_nodes == 0

    def remove(self, event: "Event") -> None:
        """Method to remove events from heap.
        The event is set as the invalid state to save the time of removing event from heap.
        """
        self.delete(event)
        self.events.remove(event)

    def update_event_time(self, event: "Event", time: int) -> None:
        """Method to update the timestamp of event and maintain the min-heap structure.
        Search for the event in nodesl,
        if event's time is needed to be:
             a) updated to an earlier time than that is scheduled -
                decrease_key(node ,key) method of fibonacci heap updates the event's time  while maintaining min-heap structure
             b) updated to an later time than that is scheduled -
                using decrease_key(node ,key) method of fibonacci heap change the event's time to -1,
                hence making it min node ,extract it from heap ,update event's time and insert into heap.
        """  
        if time < event.time:
            self.decrease_key(event, (time, event.priority))
        if time > event.time:
            self.remove(event)
            new_event = Event(time, owner=event.owner, activation_method=event.activation, act_params=event.act_params, priority=event.priority)
            self.push(new_event)