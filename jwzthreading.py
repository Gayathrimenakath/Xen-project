"""jwzthreading.py

Contains an implementation of an algorithm for threading mail
messages, as described at http://www.jwz.org/doc/threading.html.

To use:

  Create a bunch of Message instances, one per message to be threaded,
  filling in the .subject, .message_id, and .references attributes.
  You can use the .message attribute to record the RFC-822 message object,
  or some other piece of information for your own purposes.

  Call the thread() function with a list of the Message instances.

  You'll get back a {subject line -> Container} dictionary; each
  container may have a .children attribute giving descendants of each
  message.  You'll probably want to sort these children by date, subject,
  or some other criterion.

Copyright (c) 2003-2010, A.M. Kuchling.

This code is under a BSD-style license; see the LICENSE file for details.

"""

import re
import urllib.request
from collections import deque
import json
from pathlib import Path

__all__ = ['Message', 'make_message', 'thread']

class Container:
    """Contains a tree of messages.

    Instance attributes:
      .message : Message
        Message corresponding to this tree node.  This can be None,
        if a Message-Id is referenced but no message with the ID is
        included.

      .children : [Container]
        Possibly-empty list of child containers.

      .parent : Container
        Parent container; may be None.
    """

    #__slots__ = ['message', 'parent', 'children', 'id']
    def __init__ (self):
        self.message = self.parent = None
        self.children = []

    def __repr__ (self):
        return '<%s %x: %r>' % (self.__class__.__name__, id(self),
                                self.message)

    def is_dummy (self):
        return self.message is None

    def add_child (self, child):
        if child.parent:
            child.parent.remove_child(child)
        self.children.append(child)
        child.parent = self

    def remove_child (self, child):
        self.children.remove(child)
        child.parent = None

    def has_descendant (self, ctr):
        """(Container): bool

        Returns true if 'ctr' is a descendant of this Container.
        """
        # To avoid recursing indefinitely, we'll do a depth-first search;
        # 'seen' tracks the containers we've already seen, and 'stack'
        # is a deque containing containers that we need to look at.
        stack = deque()
        stack.append(self)
        seen = set()
        while stack:
            node = stack.pop()
            if node is ctr:
                return True
            seen.add(node)
            for child in node.children:
                if child not in seen:
                    stack.append(child)
        return False

def uniq(alist):
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set.keys()]

msgid_pat = re.compile('<([^>]+)>')
restrip_pat = re.compile("""(
  (Re(\[\d+\])?:) | (\[ [^]]+ \])
\s*)+
""", re.I | re.VERBOSE)

def make_message (msg):
    """(msg:rfc822.Message) : Message
    Create a Message object for threading purposes from an RFC822
    message.
    """
    new = Message(msg)

    m = msgid_pat.search(msg.get("Message-ID", ""))
    if m is None:
        raise ValueError("Message does not contain a Message-ID: header")

    new.message_id = m.group(1)

    # Get list of unique message IDs from the References: header
    refs = msg.get("References", "")
    new.references = msgid_pat.findall(refs)
    new.references = uniq(new.references)
    new.subject = msg.get('Subject', "No subject")

    # Get In-Reply-To: header and add it to references
    in_reply_to = msg.get("In-Reply-To", "")
    m = msgid_pat.search(in_reply_to)
    if m:
        msg_id = m.group(1)
        if msg_id not in new.references:
            new.references.append(msg_id)

    return new

class Message (object):
    """Represents a message to be threaded.

    Instance attributes:
    .subject : str
      Subject line of the message.
    .message_id : str
      Message ID as retrieved from the Message-ID header.
    .references : [str]
      List of message IDs from the In-Reply-To and References headers.
    .message : any
      Can contain information for the caller's use (e.g. an RFC-822 message object).

    """
    __slots__ = ['message', 'message_id', 'references', 'subject']

    def __init__(self, msg=None):
        self.message = msg
        self.message_id = None
        self.references = []
        self.subject = None

    def __repr__ (self):
        return '<%s: %r>' % (self.__class__.__name__, self.message_id)

def prune_container(container):
    """(container:Container) : [Container]
    Recursively prune a tree of containers, as described in step 4
    of the algorithm.  Returns a list of the children that should replace
    this container.
    """

    # Prune children, assembling a new list of children
    new_children = []
    for ctr in container.children[:]:
        L = prune_container(ctr)
        new_children.extend(L)
        container.remove_child(ctr)

    for c in new_children:
        container.add_child(c)

    if (container.message is None and
        len(container.children) == 0):
        # 4.A: nuke empty containers
        return []
    elif (container.message is None and
          (len(container.children)==1 or
           container.parent is not None)):
        # 4.B: promote children
        L = container.children[:]
        for c in L:
            container.remove_child(c)
        return L
    else:
        # Leave this node in place
        return [container]


def thread (msglist):
    """([Message]) : {string:Container}

    The main threading function.  This takes a list of Message
    objects, and returns a dictionary mapping subjects to Containers.
    Containers are trees, with the .children attribute containing a
    list of subtrees, so callers can then sort children by date or
    poster or whatever.
    """

    id_table = {}
    for msg in msglist:
        # 1A
        this_container = id_table.get(msg.message_id, None)
        if this_container is not None:
            this_container.message = msg
        else:
            this_container = Container()
            this_container.message = msg
            id_table[msg.message_id] = this_container

        # 1B
        prev = None
        for ref in msg.references:
            container = id_table.get(ref, None)
            if container is None:
                container = Container()
                container.message_id = ref
                id_table[ref] = container

            if (prev is not None):
                # Don't add link if it would create a loop
                if container is this_container:
                    continue
                if container.has_descendant(prev):
                    continue
                prev.add_child(container)

            prev = container

        if prev is not None:
            prev.add_child(this_container)

    # 2. Find root set
    root_set = [container for container in id_table.values()
                if container.parent is None]

    # 3. Delete id_table
    del id_table

    # 4. Prune empty containers
    for container in root_set:
        assert container.parent == None

    ##print 'before'
    ##for ctr in root_set:
    ##    print_container(ctr)

    new_root_set = []
    for container in root_set:
        L = prune_container(container)
        new_root_set.extend(L)

    root_set = new_root_set

    ##print '\n\nafter'
    ##for ctr in root_set:
    ##     print_container(ctr)

    # 5. Group root set by subject
    subject_table = {}
    for container in root_set:
        if container.message:
            subj = container.message.message_id
        else:
            c = container.children[0]
            subj = container.children[0].message.message_id

        subj = restrip_pat.sub('', subj)
        if subj == "":
            continue

        existing = subject_table.get(subj, None)
        if (existing is None or
            (existing.message is not None and
             container.message is None) or
            (existing.message is not None and
             container.message is not None and
             len(existing.message.message_id) > len(container.message.message_id))):
            subject_table[subj] = container

    # 5C
    for container in root_set:
        if container.message:
            subj = container.message.message_id
        else:
            subj = container.children[0].message.message_id

        subj = restrip_pat.sub('', subj)
        ctr = subject_table.get(subj)
        if ctr is None or ctr is container:
            continue
        if ctr.is_dummy() and container.is_dummy():
            for c in ctr.children:
                container.add_child(c)
        elif ctr.is_dummy() or container.is_dummy():
            if ctr.is_dummy():
                ctr.add_child(container)
            else:
                container.add_child(ctr)
        elif len(ctr.message.message_id) < len(container.message.message_id):
            # ctr has fewer levels of 're:' headers
            ctr.add_child(container)
        elif len(ctr.message.message_id) > len(container.message.message_id):
            # container has fewer levels of 're:' headers
            container.add_child(ctr)
        else:
            new = Container()
            new.add_child(ctr)
            new.add_child(container)
            subject_table[subj] = new

    return subject_table

messages = {}
msg = []
def msg_ids(ctr, message_list = [], depth=0, debug=0):
    """
    This function creates a message_list dictionary with messgae IDs
    as key and list of messages as value.

    :param ctr: Container object
    :param message_list: dictionary containing message ids
    :param depth:counter
    """
    for c in ctr.children:
        message_list.append(c.message.message_id)
        msg_ids(c, message_list, depth+1)

def print_container(ctr, f, depth=0, debug=0):
    import sys
    
    sys.stdout.write(depth*' ')
    c = depth*' '
    json.dump(c, f, ensure_ascii=True, indent=4)
    if debug:
        # Printing the repr() is more useful for debugging
        sys.stdout.write(repr(ctr))
    else:
        sys.stdout.write(repr(ctr.message and ctr.message.subject))
        s = repr(ctr.message and ctr.message.subject)
        #s = sys.stdout.write("asdf")
        #json.dump(s, f, ensure_ascii=True, indent=4)
        f.write(s)
        
        
    sys.stdout.write('\n')
    f.write('\n')
    
    for c in ctr.children:
        print_container(c, f, depth+1)


def message_details(filename,Outputfile):
    """
    This function
    :param filename: name of the mbox file
    :return: dictionary with messages {'message id1':[list of threads]}
    """
    import mailbox
    import os
    global mbox

    local_filename = filename.split('x/')[-1]
    print(local_filename)
    folder = '/home/gayathri/Xen/mboxes/'
    local_filename = folder + local_filename
    print(local_filename)
    #os.system('wget %s -P mboxes' %filename)

    my_file = Path(local_filename)
    if my_file.is_file():
        mbox = mailbox.mbox(local_filename)
    else:
        os.system('wget %s -P %s' %(filename, folder))
        #urllib.request.urlretrieve(filename, filename)
        mbox = mailbox.mbox(local_filename)

    msglist = []
    messages = []

    for message in mbox:
        m = make_message(message)
        msglist.append(m)

    print('Threading...')
    subject_table = thread(msglist)

    # Output
    L = subject_table.items()
    sorted(L)
    with open(Outputfile,'w+') as f:
        for subj, container in L:
            print_container(container,f)
        f.close()
        
    os.remove(local_filename)
    return container
