# edit this for later!
from __future__ import annotations

import csv
from typing import Any, Optional

from python_ta.contracts import check_contracts


# @check_contracts - We are commenting this out, so it doesn't slow down the code for Part 1.2
class Tree:
    """A recursive tree data structure.

    Note the relationship between this class and RecursiveList; the only major
    difference is that _rest has been replaced by _subtrees to handle multiple
    recursive sub-parts.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """
    # Private Instance Attributes:
    #   - _root:
    #       The item stored at this tree's root, or None if the tree is empty.
    #   - _subtrees:
    #       The list of subtrees of this tree. This attribute is empty when
    #       self._root is None (representing an empty tree). However, this attribute
    #       may be empty when self._root is not None, which represents a tree consisting
    #       of just one item.
    _root: Optional[Any]
    _subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        return self._root is None

    def __len__(self) -> int:

        if self.is_empty():
            return 0
        else:
            size = 1  # count the root
            for subtree in self._subtrees:
                size += subtree.__len__()  # could also write len(subtree)
            return size

    def __contains__(self, item: Any) -> bool:

        if self.is_empty():
            return False
        elif self._root == item:
            return True
        else:
            for subtree in self._subtrees:
                if subtree.__contains__(item):
                    return True
            return False

    def __str__(self) -> str:
        """Return a string representation of this tree.

        For each node, its item is printed before any of its
        descendants' items. The output is nicely indented.

        You may find this method helpful for debugging.
        """
        return self._str_indented(0).rstrip()

    def _str_indented(self, depth: int) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            str_so_far = '  ' * depth + f'{self._root}\n'
            for subtree in self._subtrees:
                # Note that the 'depth' argument to the recursive call is
                # modified.
                str_so_far += subtree._str_indented(depth + 1)
            return str_so_far

    def remove(self, item: Any) -> bool:
        """Delete *one* occurrence of the given item from this tree.

        Do nothing if the item is not in this tree.
        Return whether the given item was deleted.
        """
        if self.is_empty():
            return False
        elif self._root == item:
            self._delete_root()  # delete the root
            return True
        else:
            for subtree in self._subtrees:
                deleted = subtree.remove(item)
                if deleted and subtree.is_empty():
                    # The item was deleted and the subtree is now empty.
                    # We should remove the subtree from the list of subtrees.
                    # Note that mutate a list while looping through it is
                    # EXTREMELY DANGEROUS!
                    # We are only doing it because we return immediately
                    # afterward, and so no more loop iterations occur.
                    self._subtrees.remove(subtree)
                    return True
                elif deleted:
                    # The item was deleted, and the subtree is not empty.
                    return True

            # If the loop doesn't return early, the item was not deleted from
            # any of the subtrees. In this case, the item does not appear
            # in this tree.
            return False

    def _delete_root(self) -> None:
        """Remove the root item of this tree.

        Preconditions:
            - not self.is_empty()
        """
        if not self._subtrees:
            self._root = None
        else:
            # Strategy: Promote a subtree (the rightmost one is chosen here).
            # Get the last subtree in this tree.
            last_subtree = self._subtrees.pop()

            self._root = last_subtree._root
            self._subtrees.extend(last_subtree._subtrees)



    def traverse(self, answers: list[bool]) -> list[str]:
        """
        Traverses the tree to return values of leaves based on the given answers.
        """
        if len(answers) == 0:
            ans = []
            for i in self._subtrees:
                ans.append(i._root)
            return ans

        match = []

        for subtree in self._subtrees:
            if int(subtree._root) == answers[0]:
                match.extend(subtree.traverse(answers[1:]))
        return match


################################################################################
# Part 1.2 Decision trees
################################################################################


@check_contracts
def build_decision_tree(file: str) -> Tree:
    """Build a decision tree storing the animal data from the given file.

    Preconditions:
        - file is the path to a csv file in the format of the provided animals.csv
    """
    tree = Tree('', [])  # The start of a decision tree

    with open(file) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header row

        for row in reader:
            value = row
            x = value.pop(0)
            value.append(x)
            tree.insert_sequence(value)

    return tree

# P = true/false choice, M = multiple voices
QUESTIONS = [
    ('What genre?', "P"),
     ('Over 2-hours?', "M"),
]


@check_contracts
def get_user_input(questions: list[str]) -> list[bool]:
    """Return the user's answers to a list of Yes/No questions."""
    answers_so_far = []

    for question in questions:
        print(question)
        s = input('Y/N: ')
        answers_so_far.append(s == 'Y')  # Any other input is interpreted as False

    return answers_so_far


@check_contracts
def run_animal_guesser(animal_file: str) -> None:
    """Run an animal guessing program based on the given animal data file.

    This function should:
        1. Create a decision tree based on the given animal file.
        2. Prompt the user for their desired animal characteristics (use `get_user_input(ANIMAL_QUESTIONS)`)
        3. Traverse the decision tree to determine the possible animals(s) that match
           the user's inputs. You will likely need to implement a new Tree method to
           accomplish this part.
        4. Print the results back to the user. This might be "no animals", an exact match
           (one animal), or multiple animals. You can choose the exact messages you print.
    """
    tree = build_decision_tree(animal_file)
    user_inputs = get_user_input(ANIMAL_QUESTIONS)
    matching_animals = tree.traverse(user_inputs)

    print(matching_animals)
    if not matching_animals:
        print("No animals.")
    elif len(matching_animals) == 1:
        print(f"The animal is {matching_animals[0]}.")
    else:
        print(f"The possible animals are: {', '.join(matching_animals)}.")


if __name__ == '__main__':

    import doctest
    doctest.testmod(verbose=True)


    import python_ta
    python_ta.check_all('ex2_part1.py', config={
        'max-line-length': 120,
        'extra-imports': ['csv', 'random'],
        'allowed-io': ['build_decision_tree', 'get_user_input', 'run_animal_guesser']
    })
