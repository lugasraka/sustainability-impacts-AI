# 01 Computing-Related Impacts

**Lecture slides:** 12-43

## What this section is about

AI has a physical footprint before it produces an answer. The lecture follows that footprint through computation, cooling, hardware production, mining, transport, and disposal. It then narrows in on an important practical distinction: training and inference have different drivers, and the energy cost of one inference varies greatly by model and task.

## Core ideas

### The footprint is a lifecycle, not a single electricity number

The lecture's GPU lifecycle diagram (slides 12-13) separates:

- **Operational emissions:** electricity used during computation, cooling, and related data-center operations; waste-heat use and renewable supply affect this stage.
- **Embodied emissions:** mining and processing raw materials, manufacturing, transporting, and disposing of hardware.

One cited study in the slides suggests operational emissions can be much larger than embodied emissions for a GPU, but that should not make embodied impacts invisible. Mining matters, and the answer depends on the hardware, grid, utilization, lifetime, and accounting boundary.

### Training and inference are different workloads

The lecture stresses that "AI" is not one thing. Models differ in size, architecture, precision, hardware, training data, number of experiments, and serving pattern.

- Training energy generally rises with model size and the amount of computation required.
- Inference repeats whenever users request an output, so high-volume use can outweigh one-time training.
- Meta and Google are cited on slide 18 as reporting that inference emissions outweigh training emissions in their contexts. This is not a universal ratio for every model or deployment.
- The energy difference between tasks can be large. The slides use a poll comparing one text prompt with an eight-second medium-definition video.
- Efficiency gains can be overtaken by usage growth: a lower cost per request may encourage more requests. This is the lecture's rebound-effect warning.

### Frugal AI is a design choice

The lecture presents frugal AI as a way to make useful systems more sustainable, inclusive, and scalable:

- Choose a small or task-specific model when it meets the quality requirement.
- Do not assume that more parameters or more data always produce better results for the task.
- Consider local models and transfer learning where they deliver adequate performance with less total effort.
- Consider TinyML and microcontrollers for constrained tasks.
- Measure the layers around the model as well as the model itself: retrieval, agents, orchestration, repeated prompting, and unnecessary output length can add cost.
- Track both performance and resource use. The slides name Code Carbon as one possible tool for estimating project energy and GHG impacts.

A frugal system meets the task's quality, safety, latency, access, and reliability requirements with less resource use. Model size alone is not the criterion.

### Energy demand is also a grid and infrastructure question

The lecture presents a rough IEA 2026 estimate of a 250-500% increase in data-center electricity demand between 2020 and 2035, compared with a 6% increase between 2010 and 2018. It also highlights that estimates are rough and that additional supply raises further questions:

- What is the carbon intensity of the marginal electricity?
- Does the supply compete with other users or essential services?
- What are the associated land, material, air, water, and social impacts?
- Can data-center demand be scheduled or made flexible?
- Does the grid experience sharp demand peaks rather than only a higher annual average?

Renewable electricity can reduce operational carbon intensity, but it does not erase hardware, water, materials, siting, or demand-growth concerns.

### Materials and water extend beyond greenhouse gases

The lecture notes that computing chips use materials drawn from many elements and that some stocks are rapidly depleting. It then uses water as a case where direct and indirect use must be separated.

Within the stated scope, the slides report that:

- water withdrawal, consumption, and discharge are different quantities;
- direct data-center water use is currently less than 0.5% of U.S. water consumption in the cited comparison;
- indirect water use from electricity generation can be much larger, up to 80% in the lecture framing;
- projected global Scope 1 + 2 water withdrawal in 2027 is shown as 4.2-6.6 billion cubic meters;
- local stress and peak timing can matter more than a global annual total;
- the slides cite Bloomberg reporting that about two-thirds of U.S. data centers built since 2022 are in high water-stress areas.

These are estimates with specific system boundaries. Ren and Luers make the same central point: onsite cooling and electricity generation are different water pathways, and the balance depends on location and technology.

### Cooling creates a water-energy trade-off

The lecture and Ren and Luers describe several options:

- closed-loop or liquid cooling can reduce evaporative water use, but may require more electricity and create higher power peaks;
- air cooling can reduce direct water use but may consume more energy in some conditions;
- recycled water, thermal storage, scheduling, waste-heat use, and better infrastructure can reduce or shift demand;
- the best choice depends on local climate, water stress, grid mix, season, and community needs.

Heat waves are a stress test because cooling demand, electricity demand, and community water demand can rise together. The Brazil case study in slides 42-43 illustrates how data-center investment, hydropower drought risk, cooling needs, and existing energy poverty can interact even when the electricity mix is relatively renewable.

## Questions to revisit

- When does inference become the dominant source of emissions for a service?
- What is the marginal electricity source for a new data center, rather than the annual average grid mix?
- Which impacts are hidden when a calculation stops at the model API?
- Does a water-saving cooling technology shift burden to energy, land, or another community?

## Challenge: make a frugal deployment selector

Build a small local web app, notebook, or script that compares three hypothetical models for the same task. Use a transparent CSV with columns such as:

`task,model,accuracy,energy_kwh_per_1000_requests,grid_gco2e_per_kwh,direct_water_ml_per_1000_requests,indirect_water_ml_per_1000_requests`

Let the user enter request volume and a minimum acceptable accuracy. The tool should calculate annual energy, carbon, direct water, and indirect water, then highlight models that are dominated by another model with equal or better accuracy and lower resource use.

**Success check:** the output changes when request volume or grid intensity changes, and every result displays the assumptions used.

**Reflection:** Would you choose the lowest-footprint model if it were slightly less accurate, slower, or less reliable? What evidence would make that trade-off acceptable?

## Sources

- [Local lecture PDF](CCAI%20Summer%20School%202026%20_%20Sustainability%20impacts%20of%20AI.pdf), slides 12-43.
- [Kaack et al. 2022, Aligning artificial intelligence with climate change mitigation](https://www.nature.com/articles/s41558-022-01377-7).
- [Ren and Luers 2025, The Real Story on AI's Water Use](https://spectrum.ieee.org/ai-water-usage).
- [Code Carbon](https://codecarbon.io/) is mentioned in the lecture as an example of an impact-estimation tool.

The lecture also cites IEA 2026, Chien et al. 2026, Ji and Jiang 2026, Luccioni et al., and other studies. The slide citations are the starting point for checking those estimates, not a substitute for reading their methods.