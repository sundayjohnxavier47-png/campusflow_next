









# Engineer Reflections

Each engineer writes a short reflection in their own words after the work is finished.

---

## Engineer A — [full name]

*(Engineer A completes this section.)*

**One mistake I made and verified:**
[...]

**One thing I learned:**
[...]

**One improvement I received through code review:**
[...]

---

## Engineer B — [Otete Benjamin Agogo]

**One mistake I made and verified:**
I pasted my new `calculate_priority` underneath the old one instead of replacing it, so the file had two functions with the same name. The old copy also had a bug: its last line was `return "low"` followed straight away by a docstring, which Python would have joined into one string. I noticed because I asked why there were two functions. I checked the effect with a small experiment (the second definition wins and neighbouring strings are joined), deleted the old copy and the unused `import json`, and now check with `grep -rn "def calculate_priority" campusflow` that only one definition is left. The priority tests guard the final function.

**One thing I learned:**
Python keeps the last function with a given name, so a copy-and-paste duplicate can hide a bug while all the tests still pass. I also learned that I should only keep code I can explain: I asked for the regex in the ID helper to be replaced with `startswith`, slicing and `isdigit` because I could not defend it, and I showed with a small experiment that the plain version gives the same answers.

**One improvement I received through code review:**
[Write this ONLY after Engineer A has reviewed your pull request. Name the comment, the file or test it was about, and what you changed because of it. Example of the shape: "A asked me for ___ in `___`, so I ___ and added `test_____`." Do not write it until it has really happened.]