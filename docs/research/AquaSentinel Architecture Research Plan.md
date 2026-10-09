# **AquaSentinel System Architecture: Evidence-Based Research Report and Implementation Strategy**

## **Executive Recommendation**

The engineering mandate requires the design, validation, and delivery of an architecture for AquaSentinel, an explainable water-network monitoring platform. The system is designed to process sequential pressure and flow telemetry, establish historical operating baselines, detect sustained deviations using a statistical change detection mechanism, and visualize suspected-leak alerts. Crucially, the architecture must support a sequential, deterministic replay of the public BattLeDIM (Battle of the Leakage Detection and Isolation Methods) benchmark dataset within a strictly constrained five-hour hackathon engineering window.  
Based on a comprehensive architectural feasibility analysis, the recommended technical direction is a **Single-Process Streamlit Monolith utilizing Fragment-Based Execution**.  
While decoupled, distributed architectures involving independent backend processing engines (such as FastAPI) and asynchronous message brokers align more closely with enterprise production standards, they introduce unacceptable network latency, state synchronization challenges, and debugging complexity within a five-hour build constraint. The recommended architecture leverages recent advancements in Streamlit's execution model—specifically the @st.fragment(run\_every=...) decorator introduced in version 1.37.01—to simulate an asynchronous, streaming telemetry pipeline entirely within a single Python process. State management for the sequential Tabular CUSUM (Cumulative Sum) calculations and incident grouping will be securely maintained using the native st.session\_state object2, eliminating the need for external databases, caching layers, or complex WebSocket management. This approach strictly prioritizes implementation velocity and deterministic demonstration reliability while satisfying all core functional requirements of the AquaSentinel evaluation platform.  
The analysis indicates that avoiding network serialization and dual-process orchestration allows the engineering team to allocate the majority of the five-hour window to the core algorithmic challenge: correctly normalizing pressure and flow residuals and tuning the statistical drift (![][image1]) and threshold (![][image2]) parameters4. The resulting application will provide a robust, highly visual, and easily deployable demonstration of data-driven leak detection.

## **Requirements and Constraints**

The translation of the AquaSentinel solution document into formal architectural requirements demands a strict delineation between essential algorithmic capabilities and extraneous infrastructure features that threaten the viability of the Minimum Viable Product (MVP). The foundation of these requirements is dictated by the physical and simulated realities of the target dataset, the L-Town water distribution network.

### **Essential Functional Requirements**

The system must satisfy the following functional criteria to successfully demonstrate the AquaSentinel solution:

> 1. **Sequential Telemetry Ingestion and Replay:** The architecture must read the BattLeDIM benchmark dataset (simulated Supervisory Control and Data Acquisition (SCADA) data from the L-Town network) and yield observations sequentially. The L-Town network comprises 782 junctions, 905 pipes, 33 pressure sensors, and 10 flow meters6. The replay mechanism must simulate a live 5-minute sampling interval, stepping through the 2019 evaluation dataset monotonically8.  
> 2. **Context-Aware Baseline Computation:** The architecture must calculate and apply a time-of-day and day-of-week baseline for designated flow sensors (specifically p227 and p235) and pressure nodes to account for routine diurnal demand variations8. This requires isolating a training period (from the 2018 dataset) to compute hourly means and standard deviations7.  
> 3. **Statistical Anomaly Detection (Tabular CUSUM):** The system must compute baseline-normalized residuals for each new observation and execute a tabular one-sided CUSUM algorithm4. The detection engine must track cumulative deviations (drift ![][image1]) over a defined decision interval threshold (![][image2]) to flag sustained anomalies indicative of background leakages or pipe bursts4.  
> 4. **Incident Grouping and State Tracking:** When a sensor's CUSUM score exceeds the threshold ![][image2], the system must emit an alert. If the threshold remains breached in subsequent sequential ticks, the architecture must group these anomalies into a single contiguous leak incident rather than flooding the dashboard with duplicate alerts.  
> 5. **Comparative Validation Interface:** The visual interface must graphically juxtapose the CUSUM detector's performance against the raw signal and the historical baseline, rendering suspected-leak alerts alongside measurable evaluation metrics, such as detection delay6.

### **Critical Non-Functional Requirements**

> 1. **Implementation Velocity and Debuggability:** The entire end-to-end data pipeline, from raw CSV ingestion to dashboard visualization, must be implementable, testable, and demonstrable within a five-hour window. Architectures requiring complex distributed state synchronization, cross-origin resource sharing (CORS) configurations, or manual memory management are prohibited.  
> 2. **Deterministic State Evolution:** The system must guarantee that the state of the CUSUM algorithm at timestep ![][image3] is computed exclusively using data up to ![][image3]. The architecture must strictly prevent future data leakage during the CSV replay, ensuring the demonstration legitimately reflects a real-time streaming scenario. Mathematical computations must be reproducible across multiple application restarts.

### **Primary Actors and System Boundary**

The primary actor is the Hackathon Evaluator or Judge, who interacts with the visual interface to observe the simulated real-time detection of leaks across the L-Town dataset. The evaluator relies on the interface to verify the explainability of the statistical models and the accuracy of the anomaly localization.  
The system boundary encapsulates the AquaSentinel application process and the local filesystem holding the static CSV files. External cloud services, live municipal SCADA APIs, external message brokers, and third-party databases are explicitly excluded from the system boundary for the MVP to minimize deployment risk.

### **Core Inputs, Outputs, and Data Contracts**

The primary input is the BattLeDIM dataset (Zenodo record 4017659), which comprises realistic virtual SCADA measurements generated from the L-Town EPANET model, featuring pressure-driven demands modeled with specific hydraulic parameters (e.g., ![][image4], ![][image5])6. The data contracts governing the internal flow of information are defined in the following table:

| Entity | Contract / Schema | Description |
| :---- | :---- | :---- |
| **Input: Telemetry** | Timestamp (ISO 8601), Sensor\_ID (String), Value (Float), Sensor\_Type (Enum: Flow/Pressure) | Raw readings from the BattLeDIM L-Town benchmark. Key flow sensors include p227 and p235; pressure sensors are distributed across zones A, B, and C9. |
| **Input: Labels** | Timestamp (ISO 8601), Leak\_ID (String), Node\_ID (String), Magnitude (Float) | Ground truth labels detailing leaks occurring in 2018 and 20197. Loaded strictly for post-detection performance evaluation. |
| **State: Baseline** | Sensor\_ID (String), Day\_of\_Week (Int), Hour (Int), Mean (Float), Std\_Dev (Float) | Computed over the 2018 historical period. Acts as the static expected behavior lookup table during the 2019 streaming replay. |
| **State: CUSUM** | Sensor\_ID (String), Current\_Score (Float), Alert\_Active (Boolean), Incident\_Start (Timestamp) | Ephemeral state maintained across loop iterations to calculate the tabular CUSUM algorithm and group continuous threshold breaches into single incidents. |
| **Output: Alerts** | Timestamp\_Detected (ISO 8601), Sensor\_ID (String), Confidence\_Score (Float), Delay (TimeDelta) | Emitted to the user interface when a sensor's CUSUM score exceeds the configured decision limit (![][image2])4. |

### **Critical User Journey**

The architecture must seamlessly facilitate the following critical user journey during the hackathon demonstration:

> 1. **Initialization:** The evaluator launches the application. The system loads the BattLeDIM CSV files into memory, caching the immutable dataset to prevent repeated disk I/O. The system computes the time-of-day baselines silently.  
> 2. **Replay Activation:** The evaluator interacts with the dashboard controls to select a target sensor (e.g., flow meter p227) and clicks a "Start Simulation" trigger.  
> 3. **Observation Loop:** The interface enters an automated polling loop. For every tick, the system fetches the next 5-minute telemetry observation from the 2019 dataset, normalizes it against the pre-calculated 2018 baseline, updates the statistical CUSUM state, and evaluates the threshold.  
> 4. **Intervention and Evaluation:** The evaluator observes real-time charts updating via localized DOM fragment reruns. An alert is visually triggered when a simulated pipe burst induces a sustained flow increase or pressure drop. The evaluator pauses the simulation to view the performance metrics, specifically comparing the algorithmic detection delay against the ground truth labels.

### **Deterministic vs. Optional Capabilities**

To safeguard the engineering timeline, specific features must be categorized as either deterministic requirements or optional enhancements.  
Features that must be deterministic include time-series ordering, strictly monotonic clock progression during the data replay, complete isolation of CUSUM state variables per sensor, and the correct application of the specific time-of-day baseline corresponding to the simulated timestamp.  
Optional features, which should be deferred unless time permits, include multi-zone correlation, spatial pressure corroboration (deferring to single-sensor CUSUM initially), and complex parameter tuning interfaces for the drift ![][image1] and threshold ![][image2] parameters.  
Features that must be explicitly excluded from the MVP include Heterogeneous Graph Neural Networks (HGNNs), automated physical dispatch systems, hydraulic digital twins requiring live EPANET calibration during runtime12, exact pipe localization algorithms8, and unauthorized web scrapers for real utility data. Pre-localization to a specific sensor or broader area is sufficient for the scope of this project8.

## **Comparison of Alternative Architectures**

To ensure a rigorous, evidence-based selection, three candidate architectures were evaluated against the specific context of a time-constrained hackathon utilizing the static BattLeDIM benchmark. The evaluation considers not just theoretical performance, but the practical realities of software development, debugging, and deployment under extreme time pressure.

### **Architecture Options**

**Option A: Single Python Application (Streamlit Monolith)** This architecture unifies data ingestion, the baseline and CUSUM processing engine, and the visual dashboard into a single Python application utilizing the Streamlit framework. Sequential replay is handled via Streamlit's @st.fragment decorator, which allows a specific component of the UI to rerun at set intervals (e.g., run\_every="1s") independently of the full script1. State is persisted across these fragment reruns via the native st.session\_state dictionary2.  
**Option B: Python Processing Backend with Separate Web Frontend** This option adheres to traditional decoupled service design. A backend built with FastAPI ingests the CSV, runs the CUSUM logic, and exposes an asynchronous StreamingResponse using Python generators (yield) to stream the telemetry tick-by-tick14. A separate frontend (built in React, Vue, or a lightweight Streamlit app) consumes this stream via Server-Sent Events (SSE)16 or long-polling.  
**Option C: Lightweight API-Driven Application** Designed purely for algorithmic purity and future live integration, this architecture consists of a headless Python API (FastAPI) that processes data and logs anomalies to a local SQLite database or simple JSON files. The visualization layer is relegated to a minimalistic HTML/JavaScript page rendering static plots from the database, or a terminal-based Command Line Interface (CLI).

### **Evaluation Criteria and Scoring Matrix**

The options were subjected to the predefined playbook feasibility framework. Architectures requiring distributed transaction management or live municipal data scraping were immediately eliminated by feasibility gates. The remaining candidates were scored across four weighted dimensions, with secondary qualitative assessments applied to specific engineering challenges.

| Evaluation Dimension | Option A (Streamlit Monolith) | Option B (FastAPI \+ Web) | Option C (API-Driven Headless) |
| :---- | :---- | :---- | :---- |
| **Implementation Speed (40%)** | **38/40** | 15/40 | 25/40 |
| **Demo Reliability (30%)** | **28/30** | 20/30 | 25/30 |
| **Problem Alignment (20%)** | **18/20** | 20/20 | 10/20 |
| **Technical Differentiation (10%)** | **7/10** | 8/10 | 4/10 |
| **Total Weighted Score** | **91/100** | 63/100 | 64/100 |

### **Qualitative Analysis of Architectural Trade-offs**

The numerical superiority of Option A is validated by examining the qualitative engineering realities associated with each approach.  
**Debugging Complexity and Real-Time Updates:** Option B introduces massive debugging complexity. Implementing a StreamingResponse in FastAPI requires managing asynchronous tasks and handling client disconnections14. If the frontend drops the SSE connection, the backend generator may halt, or worse, continue processing and lose synchronization with the UI. Option A eliminates network serialization and CORS debugging. The @st.fragment mechanism13 handles DOM updates natively via Streamlit's internal WebSocket, abstracting the network layer entirely away from the developer.  
**Event Replay and State Management:** The tabular CUSUM algorithm is inherently stateful; ![][image6] depends entirely on ![][image7]4. In Option B, the state must be maintained in the backend memory while the frontend maintains the visual state. If a judge requests the simulation to pause or step backward, orchestrating that command from the frontend to the backend stream is highly complex. In Option A, the st.session\_state holds the simulation index and the CUSUM arrays in the exact same memory space as the UI rendering logic2. Pausing the simulation simply involves setting a boolean flag in st.session\_state that halts the fragment execution.  
**Team-Skill Requirements and Testing:** Option B requires the hackathon team to possess full-stack capabilities, including asynchronous Python programming, API design, and frontend framework expertise. Testing requires mocking API endpoints. Option A requires only fundamental Python, Pandas, and basic Streamlit knowledge. Testing the CUSUM logic in Option A is as simple as passing a NumPy array into a standard Python function, entirely decoupled from the UI.  
**Deployment Complexity and Future Extension:** While Option B and Option C offer superior pathways to future integration with real-world authorized utility telemetry, they sacrifice the immediate goal: winning the hackathon demonstration. Option A can be deployed locally on the evaluator's machine or via Streamlit Community Cloud with zero infrastructure provisioning.  
**Conclusion of Alternatives:** Pursuing Option B requires the engineering team to manage two distinct Python environments, handle JSON serialization for every tick of the 5-minute telemetry interval, and engineer a robust reconnection protocol. In a five-hour window, debugging an asynchronous generator yield loop19 introduces catastrophic failure risks. Option A bypasses the network layer entirely, focusing all engineering effort on the core statistical problem: correctly implementing the baseline and the CUSUM algorithm. Therefore, the Streamlit Monolith is the definitive recommendation.

## **Architecture Definition**

The recommended architecture encapsulates a sequential processing engine within a reactive Streamlit application. The design strictly adheres to data isolation principles, ensuring the baseline and CUSUM detectors operate solely on historical and current observations relative to the simulated clock.

### **System-Context Diagram (C4 Level 1\)**

The system context illustrates a highly contained environment. The AquaSentinel platform acts as an intermediary between the static datasets and the human evaluator.

Code snippet  
C4Context  
    title System Context Diagram \- AquaSentinel  
      
    Person(judge, "Hackathon Evaluator", "Observes network state, views leak alerts, and evaluates detection algorithms.")  
      
    System(aquasentinel, "AquaSentinel Platform", "Analyzes time-series water telemetry, applies statistical CUSUM detection, and visualizes anomalies.")  
      
    System\_Ext(battledim, "BattLeDIM Dataset", "Static CSV files containing 2018-2019 L-Town network SCADA measurements (pressures, flows, labels).")

    Rel(judge, aquasentinel, "Configures simulation and observes dashboard via", "Web Browser")  
    Rel(aquasentinel, battledim, "Ingests historical telemetry for sequential replay")

### **Container Diagram (C4 Level 2\)**

The container diagram breaks down the single-process monolith into its logical internal boundaries. While physically executing in the same Python process, separating the data ingestion, state management, and statistical engine ensures clean, modular code.

Code snippet  
C4Container  
    title Container Diagram \- AquaSentinel MVP  
      
    Person(judge, "Evaluator", "Hackathon Judge")  
      
    System\_Boundary(c1, "AquaSentinel Single-Process Application") {  
        Container(ui, "Streamlit Dashboard", "Python / Streamlit", "Renders the UI, charts, and interactive controls. Manages the simulation loop via st.fragment.")  
        Container(state\_manager, "Session State Store", "st.session\_state", "Holds mutable runtime state: simulation clock index, CUSUM scores, and incident grouping data.")  
        Container(data\_ingestor, "Data Ingestion & Cache", "Pandas / st.cache\_data", "Loads BattLeDIM CSVs into memory-mapped DataFrames for zero-latency access.")  
        Container(detector, "Statistical Engine", "NumPy / Python", "Computes time-of-day baselines, normalizes residuals, and executes the one-sided Tabular CUSUM algorithm.")  
    }  
      
    System\_Ext(fs, "Local File System", "CSV Files")

    Rel(judge, ui, "Starts replay, views alerts")  
    Rel(data\_ingestor, fs, "Reads CSVs once on startup")  
    Rel(ui, state\_manager, "Reads/Writes current simulation clock")  
    Rel(ui, data\_ingestor, "Requests data slice up to current clock")  
    Rel(detector, state\_manager, "Reads S\_{t-1}, writes S\_t")  
    Rel(ui, detector, "Passes current telemetry for analysis")

### **Data Flow from Dataset to Dashboard**

The data flow must maintain strict chronological integrity. Future data cannot influence past CUSUM states.

Code snippet  
flowchart TD  
    A\[(BattLeDIM CSVs\\n2018/2019)\] \--\>|Read once\\nst.cache\_data| B(Data Ingestion Layer)  
    B \--\>|Extract 2018 Data| C\[Baseline Generator\]  
    C \--\>|Compute Hourly Means| D\[(Baseline Profile Cache)\]  
      
    B \--\>|Sequential Yield\\nTick t (2019 Data)| E{Streamlit Fragment Loop}  
    E \--\>|Raw Observation X\_t| F\[Residual Normalization\]  
    D \--\>|Expected Value mu, sigma| F  
      
    F \--\>|Normalized Residual Z\_t| G\[Tabular CUSUM Engine\]  
    H\[(st.session\_state\\nCUSUM S\_{t-1})\] \--\> G  
      
    G \--\>|Update S\_t| H  
    G \--\>|Score vs Threshold| I{Threshold Evaluator}  
      
    I \--\>|S\_t \< h| J\[Update Time-Series Chart\]  
    I \--\>|S\_t \>= h| K\[Group Incident & Trigger Alert\]  
      
    J \--\> L((Evaluator Dashboard))  
    K \--\> L

### **Component Responsibilities and Boundaries**

To prevent "spaghetti code" within the five-hour hackathon, the monolith must be logically partitioned.

> 1. **Data Ingestion Layer:** This module is exclusively responsible for file I/O operations. It parses the L-Town pressure and flow data into Pandas DataFrames. Crucially, the main ingestion function must be decorated with @st.cache\_data21. This ensures the heavy I/O operation and CSV parsing only occurs upon the first app initialization. Subsequent reruns of the Streamlit script will read the DataFrames directly from RAM, reducing latency to near zero.  
> 2. **Baseline Generator:** Operating during the initialization phase, this module filters the dataset for a designated leak-free period. Utilizing the 2018 data, it computes a diurnal pattern matrix. For instance, it calculates the average flow and pressure for every hour of every day of the week, resulting in ![][image8] distinct operational profiles (![][image9])8.  
> 3. **Simulation Controller (Fragment Loop):** This is a specific function decorated with @st.fragment(run\_every="1s")13. It reads the current simulation index ![][image3] from st.session\_state, increments it, and extracts the corresponding row from the cached DataFrames. This isolates the high-frequency execution loop from the rest of the application UI, preventing full-page redraws which would cause visual stuttering1.  
> 4. **CUSUM Engine:** A deterministic, stateless function (computationally) that accepts the current observation (![][image10]), the baseline expected value (![][image11]), the historical standard deviation (![][image12]), the algorithmic parameters ![][image1] (allowable drift) and ![][image2] (decision limit), and the prior state ![][image13]4. It calculates and returns the new state ![][image14].

### **State-Management Requirements**

In a streaming water network detection system, algorithms cannot rely on future data to identify anomalies in the present. The one-sided tabular CUSUM algorithm specifically accumulates evidence of a mean shift over time, making state preservation critical.  
For identifying leaks in a water distribution network, the physical consequences are clear: leaks cause an *increase* in localized flow and a *decrease* in localized pressure8. Therefore, the application must track two distinct CUSUM variants depending on the sensor type:

* **Flow Sensors (Upper One-Sided CUSUM):** Detects an anomalous increase in water demand (e.g., at sensors p227 and p235).  
  * ![][image15]  
* **Pressure Sensors (Lower One-Sided CUSUM):** Detects an anomalous drop in hydraulic head.  
  * ![][image16]  
  * *(Note: ![][image17] represents the standardized residual: ![][image18])*

**State Ownership and Incident Grouping:** Streamlit's execution model inherently destroys local variables upon a script rerun. Therefore, st.session\_state assumes absolute ownership of the CUSUM state vector2. Furthermore, the state must track continuous threshold breaches to group them into a single incident. If a leak starts at 10:00 AM and persists until 12:00 PM, the system must not generate 24 distinct alerts (one for every 5-minute tick).  
The state dictionary must initialize securely before any widgets are rendered:

Python  
if "system\_state" not in st.session\_state:  
    st.session\_state.system\_state \= {  
        "clock\_index": 0,  
        "is\_playing": False,  
        "sensors": {  
            "p227": {  
                "cusum": 0.0,   
                "is\_alert\_active": False,  
                "current\_incident\_start": None,  
                "incident\_history": \[\]  
            },  
            "n549": {  
                "cusum": 0.0,   
                "is\_alert\_active": False,  
                "current\_incident\_start": None,  
                "incident\_history": \[\]  
            }   
        }  
    }

### **Processing Sequence for Each New Observation**

> 1. **Tick Execution:** The @st.fragment fires automatically based on its run\_every parameter. It verifies st.session\_state.system\_state\["is\_playing"\] is True.  
> 2. **Data Extraction:** The clock\_index is incremented. Observation ![][image10] is pulled for the selected sensor ![][image19] at time ![][image3].  
> 3. **Context Alignment:** The system determines the current day-of-week and hour of the timestamp ![][image3], retrieving ![][image11] and ![][image12] from the Baseline Profile Cache.  
> 4. **Residual Computation:** The standardized residual is calculated: ![][image20].  
> 5. **CUSUM Update:** The engine fetches ![][image7] from the session state. It computes ![][image6] based on the upper or lower variant equation.  
> 6. **Threshold Evaluation & Grouping:**  
   * If ![][image21] and is\_alert\_active is False: A new incident begins. current\_incident\_start is set to ![][image3], and is\_alert\_active becomes True.  
   * If ![][image21] and is\_alert\_active is True: The incident continues. No new alert is generated.  
   * If ![][image22] and is\_alert\_active is True: The incident concludes. The incident metadata is appended to incident\_history, and is\_alert\_active resets to False.  
> 7. **State Mutation:** st.session\_state is updated with the new ![][image6] and alert flags.  
> 8. **UI Render:** The fragment function calls charting libraries to append the new data point and update evaluation metrics.

### **Error-Handling and Fallback Design**

Architectures designed for hackathons must anticipate platform-specific quirks and gracefully degrade rather than crashing entirely.

* **Risk:** Streamlit's @st.fragment(run\_every=...) may exhibit unpredictable behavior, memory bloat, or browser freezing if left running indefinitely during a high-speed replay (e.g., thousands of ticks)1.  
* **Fallback Strategy:** If the auto-running fragment fails or stutters unacceptably during testing, the architecture will seamlessly degrade to a standard time.sleep() loop inside an st.empty() container25. This is a documented, stable Streamlit pattern for in-place updates, albeit slightly less elegant than fragments. The state management logic remains identical; only the execution trigger changes.  
* **Risk:** The CUSUM state becomes corrupted due to double-execution of a button click (a known Streamlit widget edge case)3.  
* **Mitigation Strategy:** State mutations will only occur strictly bound to the monotonic clock\_index. The clock\_index will act as an idempotency key; if the statistical engine receives a recalculation request for an index it has already processed, it will instantly return the cached result rather than double-adding the residual to the CUSUM score.

## **Minimum Viable Infrastructure Assessment**

A critical flaw in many data engineering hackathon projects is the over-provisioning of infrastructure, leading to hours wasted on Docker configurations, networking, and cloud IAM roles rather than algorithmic value. The assessment of AquaSentinel's Minimum Viable Infrastructure (MVI) concludes the following:

| Infrastructure Component | Status | Architectural Justification |
| :---- | :---- | :---- |
| **Separate Backend API** | Excluded | Not required. The Streamlit process is highly capable of executing Pandas/NumPy vector operations and the CUSUM math in the same memory space as the UI thread. |
| **Relational/NoSQL Database** | Excluded | Not required. The 2018/2019 BattLeDIM dataset (spanning hundreds of thousands of rows) can be loaded entirely into RAM using Pandas DataFrames. Mutable runtime state will be held in st.session\_state2. |
| **Message Broker (Kafka/Redis)** | Excluded | Unnecessary overhead. There are no competing consumer groups, distributed workers, or microservices requiring message queuing. |
| **WebSockets / Server-Sent Events** | Excluded | Replaced by in-process loop execution. Streamlit's fragment execution model automatically pushes DOM updates to the browser via its internal WebSocket without requiring custom configuration by the developer3. |
| **Background Workers (Celery)** | Deferred | The data replay is triggered manually and runs synchronously within the fragment loop. Complex job queuing is unnecessary for sequential CSV replay. |
| **Cloud Deployment** | Deferred | The application should be designed to run on localhost to eliminate reliance on hackathon venue Wi-Fi stability and cloud provisioning times. |
| **Authentication/Authorization** | Excluded | Out of scope for a localized MVP demonstration. |
| **LLM or Generative Agent** | Excluded | The solution explicitly relies on explainable statistical change detection (CUSUM) and empirical baselines, avoiding opaque generative AI models which hallucinate or fail to provide mathematical guarantees. |

If sequential CSV replay and an in-process processing loop satisfy the demo requirements—and the analysis confirms they absolutely do—then standing up databases and APIs is engineering malpractice for this specific five-hour constraint.

## **Verification of Technical Recommendations**

All architectural recommendations and design patterns are grounded in verified documentation and explicit capabilities of the target technology stack. To prevent assumptions from jeopardizing the build, the following claims have been verified against authoritative sources.

| Technology / Concept | Verified Capability | Source / Justification |
| :---- | :---- | :---- |
| **BattLeDIM Dataset Structure** | L-Town dataset (Zenodo 4017659\) consists of realistically simulated SCADA data. 2018 contains training data with resolved leaks; 2019 contains evaluation data with unresolved leaks6. | The architecture's strict separation of a 2018 offline baseline generator and a 2019 sequential replay engine perfectly maps to this dataset structure8. Verified via multiple academic implementations. |
| **Streamlit State Persistence** | st.session\_state persists Python dictionaries and primitives safely across user interactions and script reruns2. | Unverified assumptions about global variables often crash Streamlit apps. Using st.session\_state is the verified, authoritative method for preserving CUSUM values. |
| **Streamlit Fragments** | @st.fragment(run\_every=...) allows a specific function to execute at set intervals, updating its isolated DOM elements without a full app rerun1. | Replaces the need for complex WebSocket/SSE architectures16 for streaming visualization in the MVP. Introduced in version 1.37.01. |
| **Streamlit Caching** | @st.cache\_data reliably stores the results of heavy data loading (e.g., parsing massive CSVs) and returns a copy to prevent mutation21. | Ensures the 5-minute telemetry file doesn't freeze the application when the user interacts with the UI. |
| **FastAPI Streaming** | Supports StreamingResponse using an async generator with yield14. | Investigated and verified, but explicitly rejected for the MVP due to implementation complexity and network overhead within a 5-hour constraint. |
| **Tabular CUSUM Algorithm** | A robust statistical method relying on reference value ![][image1] (allowable drift) and decision interval ![][image2]4. | Verified as a suitable algorithm for detecting the sustained, subtle mean shifts characteristic of background water leakages4. |

## **Sources, Uncertainties, and Unresolved Decisions**

While the architecture is highly deterministic, certain uncertainties remain that must be resolved empirically during the hackathon implementation phase.  
**Uncertainty 1: Dataset Scale and Memory Limits** While Pandas can comfortably hold millions of rows in memory on modern hardware, the exact memory footprint of the entire 2018 and 2019 BattLeDIM dataset (encompassing 33 pressure sensors and 10 flow meters at 5-minute intervals)7 is not strictly quantified in the snippets. *Resolution:* The data ingestion layer should be designed to filter the CSV files immediately upon reading, discarding data from sensors not actively selected for the demo (e.g., focusing only on p227, p235, and a subset of Zone A pressure nodes)9.  
**Uncertainty 2: CUSUM Parameter Tuning (![][image1] and ![][image2])** The architectural design accommodates the CUSUM algorithm perfectly, but the mathematical effectiveness of the algorithm depends entirely on empirical parameter tuning. The reference value ![][image1] is typically chosen as half the expected mean shift magnitude, and ![][image2] is typically 4 or 5 times the standard deviation4. However, the specific hydraulic variance of L-Town flow meters is unknown prior to data analysis. *Resolution:* The UI must include slider widgets (outside the running fragment) that allow the evaluator or engineer to dynamically adjust ![][image1] and ![][image2] during testing to visually observe the impact on false positive rates and detection delay.  
**Uncertainty 3: Nominal vs. Real Hydraulic Models** The literature notes that the BattLeDIM competition provided participants with a "nominal" EPANET model, while the data was generated from a secret "real" model containing structural uncertainties8. *Resolution:* Because the recommended architecture utilizes a purely data-driven statistical approach (baselines derived from actual 2018 measurements) rather than a model-based hydraulic digital twin, these structural uncertainties are inherently bypassed. The architecture learns the "real" behavior from the data, nullifying this uncertainty.

## **Explicit MVP Inclusions and Exclusions**

To safeguard the 5-hour delivery window, the engineering strategy demands rigid boundary management. Scope creep is the primary risk to hackathon success.

### **Explicit Inclusions (Must Build)**

> 1. **Data Loader Module:** A cached Pandas ingestion script targeting the 2018 and 2019 BattLeDIM CSV files, filtering for critical flow sensors like p227 and p235, and representative pressure sensors8.  
> 2. **Time-of-Day Profiler:** A processing block grouping historical 2018 data by (day\_of\_week, hour\_of\_day) to compute ![][image11] and ![][image12].  
> 3. **CUSUM State Machine:** A Python class or set of pure functions managing ![][image23], ![][image24], and incident grouping utilizing st.session\_state.  
> 4. **Dashboard View:** A split-pane Streamlit layout. The top pane displays the raw telemetry signal overlaid with the computed baseline. The bottom pane displays the CUSUM score plotted against the horizontal decision threshold ![][image2].

### **Explicit Exclusions (Do Not Build)**

> 1. **Hydraulic Modeling (EPANET/WNTR):** Using WNTR or EPANET to simulate nominal pressures in real-time is computationally expensive and overly complex for a 5-hour MVP12. The architecture relies strictly on data-driven statistical baselines.  
> 2. **Heterogeneous Graph Neural Networks (HGNNs):** Deep learning requires extensive hyperparameter tuning, GPU dependencies, and acts as a black box. This violates the "explainable" requirement of AquaSentinel27.  
> 3. **Exact Pipe Localization:** Determining the specific leaking pipe out of 905 pipes requires multi-sensor spatial correlation matrices, PageRank algorithms, or complex graph traversal7. The MVP will only alert on the *sensor* detecting the anomaly, which constitutes valid pre-localization8.  
> 4. **Live Municipal Telemetry Adapters:** Building OAuth/API connectors for real-world utility databases is deferred until post-hackathon commercialization. The MVP relies solely on the BattLeDIM CSVs.

## **Implementation-Ready Architecture Handoff**

The architecture is feasible, highly aligned with the constraints of the BattLeDIM dataset, and optimized for a high-impact, deterministic technical demonstration. The engineering team must execute the following sequence immediately upon commencement. Do not deviate into building backend APIs, deploying Docker containers, or training neural networks.  
**Phase 1: Ingestion and Baseline Construction (Hour 1\)**

* Write a Python script to load the Zenodo 4017659 dataset using Pandas.  
* Filter the dataset immediately for flow sensors p227 and p2359.  
* Group the 2018 data by day-of-week and hour to calculate the mean (![][image11]) and standard deviation (![][image12]). Save this as a lookup dictionary. Do not proceed to UI development until this data can be printed to the terminal successfully.

**Phase 2: State and Logic Core (Hours 2-3)**

* Implement the CUSUM mathematical function in standard Python (no UI code yet). Ensure the function correctly branches for flow (upper one-sided) and pressure (lower one-sided)4.  
* Initialize the st.session\_state dictionary to hold the ![][image6] accumulators, the simulation index, and the incident history list.  
* Write rapid unit tests passing mock arrays through the CUSUM function to ensure it triggers and groups incidents correctly when fed an artificial mean shift.

**Phase 3: The Streaming Fragment (Hour 4\)**

* Create the main Streamlit UI.  
* Wrap the sequential execution loop in @st.fragment(run\_every="1s")1. Inside this fragment, pull the next row from the Pandas DataFrame based on the session state index, calculate the residual, update the CUSUM score, and append the results to a visualization buffer.  
* Use st.line\_chart or plotly to render the buffers dynamically within the fragment.

**Phase 4: Tuning and Polish (Hour 5\)**

* Adjust the drift parameter ![][image1] and decision threshold ![][image2] until the detector successfully flags the known 2019 BattLeDIM leaks without excessive false positives.  
* Finalize the comparative validation UI, clearly displaying the time between the start of the leak incident and the algorithmic detection alert6.

By rigorously adhering to this single-process, state-managed Streamlit architecture, the engineering team minimizes system integration risk, maximizes time spent on statistical accuracy, and guarantees a reliable, deterministic streaming replay of the AquaSentinel solution.

#### **Works cited**

> 1. Working with fragments \- Streamlit Docs, [https\://docs.streamlit.io/develop/concepts/architecture/fragments](https://docs.streamlit.io/develop/concepts/architecture/fragments)  
> 2. Session State \- Streamlit Docs, [https\://docs.streamlit.io/develop/api-reference/caching-and-state/st.session\_state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)  
> 3. Button behavior and examples \- Streamlit Docs, [https\://docs.streamlit.io/develop/concepts/design/buttons](https://docs.streamlit.io/develop/concepts/design/buttons)  
> 4. Cumulative Sum Quality Control Charts Design and Applications, [https\://open.uct.ac.za/server/api/core/bitstreams/2152d98f-83f2-40e4-ab5d-43d71c30d3a0/content](https://open.uct.ac.za/server/api/core/bitstreams/2152d98f-83f2-40e4-ab5d-43d71c30d3a0/content)  
> 5. (PDF) Distribution-Free CUSUM-Type Control Charts for Monitoring, [https\://www\.researchgate.net/publication/353326299\_Distribution-Free\_CUSUM-Type\_Control\_Charts\_for\_Monitoring\_Industrial\_Processes\_An\_Overview](https://www.researchgate.net/publication/353326299_Distribution-Free_CUSUM-Type_Control_Charts_for_Monitoring_Industrial_Processes_An_Overview)  
> 6. Battle of the Leakage Detection and Isolation Methods, [https\://research.tudelft.nl/files/143790946/\_ASCE\_WR.1943\_5452.0001601.pdf](https://research.tudelft.nl/files/143790946/_ASCE_WR.1943_5452.0001601.pdf)  
> 7. The performance of encoder–decoder neural networks for leak, [https\://iwaponline.com/ws/article/24/8/2750/103665/The-performance-of-encoder-decoder-neural-networks](https://iwaponline.com/ws/article/24/8/2750/103665/The-performance-of-encoder-decoder-neural-networks)  
> 8. Battle of the Leakage Detection and Isolation Methods \- ResearchGate, [https\://www\.researchgate.net/publication/364293441\_Battle\_of\_the\_Leakage\_Detection\_and\_Isolation\_Methods](https://www.researchgate.net/publication/364293441_Battle_of_the_Leakage_Detection_and_Isolation_Methods)  
> 9. Assessing the Contribution of SCADA-Derived Pump Operating, [https\://www\.researchgate.net/publication/410924149\_Assessing\_the\_Contribution\_of\_SCADA-Derived\_Pump\_Operating\_Regimes\_to\_Leakage\_Assessment\_in\_Water\_Distribution\_Networks](https://www.researchgate.net/publication/410924149_Assessing_the_Contribution_of_SCADA-Derived_Pump_Operating_Regimes_to_Leakage_Assessment_in_Water_Distribution_Networks)  
> 10. Leak detection and localization in water distribution systems via, [https\://pmc.ncbi.nlm.nih.gov/articles/PMC11647635/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11647635/)  
> 11. Data-driven Leak Localization in Water Distribution Networks via, [https\://upcommons.upc.edu/bitstreams/33dd362f-7d66-4b1f-870f-3e6554738cb4/download](https://upcommons.upc.edu/bitstreams/33dd362f-7d66-4b1f-870f-3e6554738cb4/download)  
> 12. Bridging the Gap Between Model Assumptions and Realities in Leak, [https\://www\.mdpi.com/2073-4441/17/24/3502](https://www.mdpi.com/2073-4441/17/24/3502)  
> 13. st.fragment \- Streamlit Docs, [https\://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)  
> 14. Custom Response \- HTML, Stream, File, others \- FastAPI, [https\://fastapi.tiangolo.com/advanced/custom-response/](https://fastapi.tiangolo.com/advanced/custom-response/)  
> 15. Stream Data \- FastAPI, [https\://fastapi.tiangolo.com/advanced/stream-data/](https://fastapi.tiangolo.com/advanced/stream-data/)  
> 16. Server-Sent Events (SSE) \- FastAPI, [https\://fastapi.tiangolo.com/tutorial/server-sent-events/](https://fastapi.tiangolo.com/tutorial/server-sent-events/)  
> 17. Release Notes \- FastAPI, [https\://fastapi.tiangolo.com/pt/release-notes/](https://fastapi.tiangolo.com/pt/release-notes/)  
> 18. st.rerun \- Streamlit Docs, [https\://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun](https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun)  
> 19. कस्टम Response \- HTML, Stream, File, अन्य \- FastAPI, [https\://fastapi.tiangolo.com/hi/advanced/custom-response/](https://fastapi.tiangolo.com/hi/advanced/custom-response/)  
> 20. Benutzerdefinierte Response – HTML, Stream, Datei, andere \- FastAPI, [https\://fastapi.tiangolo.com/de/advanced/custom-response/](https://fastapi.tiangolo.com/de/advanced/custom-response/)  
> 21. Caching overview \- Streamlit Docs, [https\://docs.streamlit.io/develop/concepts/architecture/caching](https://docs.streamlit.io/develop/concepts/architecture/caching)  
> 22. Create a fragment across multiple containers \- Streamlit Docs, [https\://docs.streamlit.io/develop/tutorials/execution-flow/create-a-multiple-container-fragment](https://docs.streamlit.io/develop/tutorials/execution-flow/create-a-multiple-container-fragment)  
> 23. Start and stop a streaming fragment \- Streamlit Docs, [https\://docs.streamlit.io/develop/tutorials/execution-flow/start-and-stop-fragment-auto-reruns](https://docs.streamlit.io/develop/tutorials/execution-flow/start-and-stop-fragment-auto-reruns)  
> 24. 2026 release notes \- Streamlit Docs, [https\://docs.streamlit.io/develop/quick-reference/release-notes/2026](https://docs.streamlit.io/develop/quick-reference/release-notes/2026)  
> 25. Update and replace elements \- Streamlit Docs, [https\://docs.streamlit.io/develop/concepts/design/animate](https://docs.streamlit.io/develop/concepts/design/animate)  
> 26. Execution flow \- Streamlit Docs, [https\://docs.streamlit.io/develop/api-reference/execution-flow](https://docs.streamlit.io/develop/api-reference/execution-flow)  
> 27. Graph Neural Networks for Pressure Estimation in Water Distribution, [https\://www\.researchgate.net/publication/382113091\_Graph\_Neural\_Networks\_for\_Pressure\_Estimation\_in\_Water\_Distribution\_Systems](https://www.researchgate.net/publication/382113091_Graph_Neural_Networks_for_Pressure_Estimation_in_Water_Distribution_Systems)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAcCAYAAAC3f0UFAAAA50lEQVR4Xu2SqwpCQRCGR1BQvIMogu9gspgtFrMYbOIj+AQWu5itYrcYThRMBqNBsVoNgpf/dy8c1j1dwQ++sDNzdmdnj8hvU4cneINDJ/dBCW7hFTacnBcWH2DFTfi4wCWMuwkfTzhyg1E8YCu0jsFEaG3JwjOs6TUvuYMrmDFFhg4cwyacwBRsww3Mh+resHABpzCtY2yhais0TK5FXZDj64na2Qv7ZL9FOIB3OJOIEXICnAThZQJ4FNVCX8csnC1bIKZ4L+oXmMOkzr2P4qvx9YjpP4A52NVxS0FCX2t4QtmJ/fk2XgTqIybkPiUQAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAZCAYAAAAFbs/PAAAAyklEQVR4XmNgGF5gNxA/AuJXQPwAVQo3KAfi/1CaIGAB4jVA/BuIbdDksAJpBohT7gKxOKoUduACxP8YILaAbANp4kBRgQa2MkDcD/K0O1SsFSoWAVOEDJ4D8U8gtkUSwxsIIIn5QMwI5YNoEB8k7glThAxAEulIfBEgvgrET4BYEUkcDJSA+DQQCyKJTWFAdb8mkhyDHxDPQRZggJh8nQESWiCMYgsoNKKRBYDgKxAvBWJmIC5jQPgNDHiQOVAAUiAMxSiKR8HAAwBOoyQQQpcK6wAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAeCAYAAADgiwSAAAAAo0lEQVR4XmNgGOpABV0ABhSBeCG6IAy0ArELuiAIcADxViCWRhbMA+L/aPgnEFuCJHmAWBKII4D4H5QtBsTMIEkYKGeA6MIALEC8Boifo0uAgDgQ3wXiA2jiYGADxL+BeBK6BAgUMUDsC2KAWAFynDBIAmbfWyDWBGJjIF4MxJxgbQyQIHvIAPHGKiA2g0mAgC8QfwTiDUDsiSwBA7DAGAXIAAD8ORoJ0Ewr5QAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAaCAYAAAAJ1SQgAAAB5UlEQVR4Xu2WPS8FQRSGjyAhiK9SNDqFKBANFQURCiREpdNIJAqF3h8QlY9Sp5PQKIRGVCJRqUhQCAkJBQne1+y6c4+d+y173cyTPJk7c2b37pydnRkRj8fznxmG63ALXsOz4Dfb6AJs/ukdPw2Sx/O0w0m4Da/gbFAPfYMvcCToHzed8BPeink5tuewI9HVzSrc1I1gCH7AS9iqYnEwKGawUR7A+kTXaNrgnZisacbF3Ogd9qlYHKzoBlALp3SjizExA2rUAbAmJnYqeXwrBWRG1cvgEqxU7U6YLQ4oCn4b/G5HdaBI6IXHutEFp8Ch/B5sOeyHT2JW7FxokeTFLp0DksUbEjPTTuC0DrgIp/CFDig4XZhFLmTdKhYHXIg40B1YoWJOwinMi1IxAfdhU1CyHifhLrGsAy7sKTyXHEoizCJXZsKS9bTL/B/CGcbnXtQBF+GW8wp7VMyGsZugJNyCuHBFbVU2zL7eC1N5BOu+r0wN+3BR4jUZL5wbYi7YE/OWXfCGPEV1BXWWrGf8RwWGSX6WDAdrd7atsTtZFNtgecR9EPPMue4UTnhDJsce7KOYo1sccGfgtsj/5xZZUJjJe0lkkW+UmWV7yVENd+F8UGfJOttLlioxB4psTjkej8fjieILaBNxzLr0IFMAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAaCAYAAADloEE2AAACfUlEQVR4Xu2YS8hNURiGX2EgJBGlJHLJiIFLImYil4GUicE/MzRQZCwjAyVFfgZIJjIhFOXIiIEYiFwKiSSJYkAu79u3Fst3zj7W5vfvVfZTT539rdW+fHutb619gJaWlpbmWEuP0GP0Gb0dfismt9NJP3qXxWg6B3Z/I1ybUHysi42k01yskvl0Mz1Fn9KBcCwP0E/0A10X+peAErGevqLP6Tf6iK5KO5Fd9Au9AXvRV2DPcyjtlIMScdQHyRr6lT6k011bU2ykd+jscLwFloS3dEnsBEuOEpe6j45J+vyWWfQlXeAbyCbYST/TFa6tKTTCdU/Hk1i8zzdJTMmRf4XehE480cU1fA+Gtpsop/acg93TjiS2IcRUAiJDkpy9sBN7NGxfwOapLl4KKqrjXWwb7BmeJLGYnHmwmrMV3QW6L+NoB93J0Q3co+9gK9qfshQ/C3yudVENuQR7hj1JXIlRuTgLKxnX6GPYIpRFnFJ3fUMfdKGr9Dwd5dqaQIX4Ip3gGxxVA6GSOKXO+IYKYh3S6qalsdf+YjiZQU8ib7roReo5s5KTZlJzNofJsFGm1aFpNFIuwzaDQg+/PPxeBFvVTsCeM6IVLis5cQn/SBe7tio0pXTR3P6HYTdTxxxUZ1RkdycxrbaqLyLucV7TuSFWa1oNwjpewK/Z7Ycu2kF+/3/BTnQnNBrLwxR6na4Ox5r+A6FP3x2y3v57dJ84Z97qM6PXTno4iZvAXqoWRhbS+7CFowPbRdfeIddBbyO3PpWA6tFK2D5tqmsbcvSBV8pnRHFoSKuQt/RA+6KWBFX+W3Q/Xeba/ntm0gf0NMr4XCgO7WtK+cuipaUwvgOCH5332aHPWAAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAaCAYAAABYQRdDAAABT0lEQVR4Xu2TTytEURyGf0IRKZQ/RQ1JUf6UDzAWtnasfAAbe7Gakm/BwkJZSFkodooVZYUsWLDwAZSFhXjeOTN1/Lpz5w6T1Tz1NHPfc+ade88516xBCk3Yi4PYGeWt2BFdZ0JlJ/iJX/iKH5jDdtzBlfLkLAzgER7jFDaXcn3e4Bm+4Uwpr8osvuC7hbv1bFm482vsdmOJXFn4wYYlFwqt7bPV8OgqvMU+PxChUv35hB9IYsRC6ZofcKh0ycJmVWXVwjrO+YHfovN3jvtWeS1rply65/IkDrArup7HO+yPsiIteGjZSgvuetvCS9Lm8iLaoFNL34AcDrtMhQWX/UCv5BNOu3wSL3DZ5ULzh3wYk8dHC0frAXfxHi9xPJoXU/HRY/R+62DrLC5awgZEqGzTh39lFBdK37VkafuRGRWqeAzXrY5nvMfqWNbgn/kGuUEwq3amsOcAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACcAAAAaCAYAAAA0R0VGAAABh0lEQVR4Xu2VzSsFURjGX6GIFMpHUUNSlI+ysGRhbUUpC0sbe7G6Jf8FCwtlITvFTrFyiw2yYMHCH6AslK/n6czN6W3uzDnqzF2YX/26d95zuvPcOe85I1LwD6mDnbAXtlr1RthiXecKQ03DT/gNX+A7jGAz3IHLlcl50gOP4Bccg/VxnZ9X8BS+wom4nhuT8Bm+wXk1RrbEPMkybFdjQbkUc+MNMcuaBHvvSWqwpAx2A7v0gAXD8U+M6IGQDIgJt6YHFAy3IGZT5MaqmD6b0gO1hufXGdyX6r0Wiggu6aJNJdyeqidxANus61l4C7utWhZNYjbdNfyQjPs2wEPJmBRTUtfb8FjMDV3h6vDt4vxQuBFOJL3RI9ivagxWUjVXnMMRvqoe4biqj8JzuKjqhPP7dNERr3Az8EHMkXIPd+EdvIDD1jwbvaRcLh411Rz6neoXjvD9yQOWP7Qi6Y3OUJuqFjScD4NwLv7OVkjr1ySChmMwBuTTWBf/MzJoONIh/qEKCgr+wg/xDkM7bdXojAAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAYAAADJ9/UkAAAB1UlEQVR4Xu2UPSiGURTHj1CEJFJKKUmRUD6ixKIwGEyUMlgsMlhkUBajslksBoNMBrO3LGKwUPKRj0QMRDGQj///Pc/jvc99ryuL6fnXr+e555znnvvce88RiRVLJANUgUzbYYgxpaA9eHcpB9SBfNvhEiepBevgHJRFvCl1gZOAZbAIsg0/Fz0BbsEqeAJLIM+IiYgfc4VN4BlciDv5g+hEWcGYMZ9g7DtCZBv0G2OqA1yDBssekS85E36AbsPG3ZoFhYaN344bY4rzXgbPH+VLXgmuQLllt3UKXsGopO4NF7Mvek9+lC95H9gFbWAT3Iuea64ZBC2IHgXZEd2pM9BjBrnkSz4luu29lp1JhixbPTgE76L+PVAdiXDot+SubefkG6KlRQ2CG9E/Zmy4C0egIohxypd8EhyAEsvOic14HgUXEIrvj6Jx84Y9Tb7kPPMtUGDZ7eS8F0Upd1KtomWaEE/T8SXnbXfZmdxMmJD0BCzJFXH7kmIAL9MbuAONUXdSvEDTkmqprG/7LNlM2IjCKmAst54lyLadprBT2SQkutIR8ALWwIxo7dYYfqpFtPVyl+ZEb/qxuH/mzyoGA2AYdFq+UGzXzaIlyKfZ+2PFivW/+gJ8UGxj1+tRCQAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAbCAYAAACX6BTbAAABTklEQVR4Xu2UvStHURzGH3mJDApFGYxSXgYx8QdYLBRl9B8YLBabmRIpNlkMFlEsUv4DkTKwSjZFeXke33PyvScK55bS71Of7r3n+d3zdr+/A1T4a0boDl13rtCukPcm2UZo/xYddILO02d6Qsdpo8tf6ANdo1Oh/Uc00IOg7iNV9Ji2u7ZfoVnd0x7XplV0uucsXuk5HaOXdKgY5/EIG+AWJXcstOfqXBVUk2TZHME6T/c+mya6RC9gAywU0gxqYXWs6zI+Pmyb/5FDf7Iz2p8GHtXxHD2EzVzEmtcA26EtRRNQ9uV3UceTdJ82J5lqPu59yil9ojewd/uKsS1/FdbBDGygiO4H6F3I610muukVHUza3xmFveSdDVkd3f0kVxXF82Yatt+t4blUtN9bKK62NK7pMG2Blas/6LLZo4t0EyUeapFq2Kx1rfCfeQMvi0TNq1b4CgAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAAA0ElEQVR4Xu2RvQ4BQRRGr0JICAohQrWdSqETpSdQaDyAR5DovYFerbedsNGqlTqJXtCIn+/unZ3czGbVij3JKebMT2ZniVL+kSwsuzEJXriHJ1hXvW1ajA68wg0sqD6FHzW2LOEbDlRrwTM8qGY5wgv0VOPNfAgfFuMJfZhXbU5ynbFqFp6YqXERBvAOuySbctFkk2TDAmZM25kWwBIcmh7Cd30Z13AFeyQH3OCW5B9Z+OkmJPdvwJqaqzjjcBF/bF/HX0RvXXUnkhjBhxtTFF9yNiRQU2KS/gAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAbCAYAAABIpm7EAAAAqElEQVR4XmNgGAXDAmgB8QogfgbE/9FwL5I6MOiESvwC4kdQNgiDNIP48QilDAysQPwXiPOBmBkqNh+I/wGxB0wRMvAD4glAzIgk5ssAsaEcSQwMOIF4BxDroImnM+DQYAnEP9EFgeA6FIujS+gD8Sd0QQaIn4LRBUEA5KTNQMwP5YP8AfJTMZSNFcgA8R0gngvE54D4JAMexTAgAMSSQMyDLjEKBh8AAOrWIOjXAi92AAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAaCAYAAAAwspV7AAABb0lEQVR4Xu2VsStFURzHf2Ig1FMWpd4tk8VkeTKKiYSiLBZZlGLyX8goi2Sz2pWyGExSYlAmAxkYeA/fr3Nvzvt11A/v3luv+6lPr/s7p/e+7/zOPUekoElph32wFD+3wO74Mxf64Su8gw/wGs7CA9jmzcuMYXgPO+NnrswEfIfryaQs4Qpdwi09AN7gqC6mDffLibiWMZzmUHJoHTf1LfyAS/VDX4zoQhbwbTsSF4puwAHY6k/KgylYk+9g9AnO+5PyJIJr8FlcuEYSwQVdDMH2hViVcKhdXTCwCc9hFe6psSCTuhDDug7VA1dUzQLPvi54LIZQPA5+CrUo7uD0GYQVVbNiDjUDH6X+tee/2odXsOzVybb8/Q40h+KPLMMXeAZ3xF01p+I2pQ9bxzk+vXAazgVknWdggikUz6GkFVydcXEtiyS8Gmzdjao1PNRvYeAL2AGH1JiFVEKx1bwHeaCOqTELqYQi/OKCgoL/8An960Keu2TZMQAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABTElEQVR4Xu2TTytFQRjGH7EgqRs2SlHUzcqGBSk7bFigLGxsZKN8BR9BlrKRpGTrEygbCyupGwtlZUEWbOTP85jhvmfOmXuNsru/+tU5z8y8Z2bODNCA9NCSeW/yJtFLj+gdfaDXdJIu0BbTry4j9J5u+XfNZNpn79+dfoNmdAVXKFzOJn0Nsigd9BRuaSoaMkuPwzCGNvuWftAV5Gc2RMeDLEorPYErJi/oAG22nVKYo2+oFpRPdAn5mSahwRv0Ga7obra5NlpmEetwxfZMVqaXdNhkGfS3ilCuYtsmW4Yr1m2yH3QsYsU0UId1xmQqfIjIbZinj8j/+n1aoX0m0xG5oaMmy6AvrdIXek534PbojPZXu31Rc4k6R2P+uZ1OwQ1YRPFx0IcPUNyWjGa+5p8HaadpS0ZXboJ2wV3+tkxrItoWFfrzNWvwT3wCEYM23mkDae8AAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,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>

[image16]: <data:image/png;base64,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>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAaCAYAAAC3g3x9AAABN0lEQVR4Xu2TPUtDMRSGjxTBTi1uBaFUWhAcLYLSsVs3dXB0cJKCUMRBly4d/QNFcXfpJDiIv6CgOAoOOji4dOoo+r6c3JCGWO8HQoc+8MBNTnjJSXJF5vwHJXgBr+ATfA/4alfHYB9+w0d4BPeMh/DD1O7t6j9YgNdw5BfApWjYA1z2ar/ShDdw0Znjdxe+wLIzH4sTuOOMueNT0Z3VnflUMKwNvyR8BInZFQ0bw5ZXS8ymaNiB6E4Jz3Ib5s04Ngxjizy7KIxswDtYMOMlOIAduyJAVfQ2eQk5r9Y1RqzCN9GXEYRPIgrrezXyDBvOmEH8YyrOnIVtMGgI10R/P1qDZ/BTJndHbkVrQc5FA6e5ZVcrU9tNA9td8SezwJZ50/yveZmZYFBP9Fkdw/XJcjqKosFzZp0fi1U8iS3B07cAAAAASUVORK5CYII=>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAaCAYAAABByvnlAAAD7ElEQVR4Xu2ZW6hOaRjHHxkyjTPNELWRm9E4lFKjSTuHIjnEjZIrF1yIGkVJ01fTROZmciyFXDgk5UIiXJASKYci5dBErpREKYccnl/P99rvfvb7rb2+bX37YK9f/bP386611/u+z/sc1iJSUlJSP32r6i30kY6td0BVDaWfao/YJHsLrPWIaogfyIB7dqlW+IEiwRn7VAf8gPKD6i+xsf2RtquGqmaKLSoe26bqz809gL9VZyW/U8aoLqvG+4EiWa56rJroB8Qc0ix2Is6oPqsOq+aIOZIJ/qv6pHqvWqmazI09hBGqa6pNki87sA9ESJ5rO8TPqruqirOn+E3MIZXIxsRYDKdmbGTvSbDJr1XT/UCCU6r53lgkl8ROft4iRSTglJBD76iaWoZ7LDtVz7wxQcUbiuaNaos3ZkB445BzqlXSfZ1B5A7zxgyWia0rC/4eWaKhMIkF3pjBOrF70P9urDuxVSyaY34UO0iDnR1IVxzOLEhV/I0UHIBZqufSsj+xVrdcmg2TyJM7A3QXhDYP2e3Gugs/qS6K1YUY1nlSrFHxjFY9kdrFGvtBb6xCh3ZcbE+eijU3/Pyx+vtt1eyvV7cDk2Ayebmu2qF6J+2HeB6oXTw/r/K8yC0Wmxt1IRDeOf6IbDEDxeop/6ZYI+kDuFEsEtc6+2bpwP6wuHoc0iTWIofQ54G1QhiaVb94o2OhWMvNScqjPJ0cjmButOCBkap7Ym16iiyHsMbTqrl+QLlflV9nmEPd5HUIzrgR/U6XxQN/j2yefyR/91YUFF7m+UL1a2QnMj5IOl3BINUVSTuENV6Q9Msj0XFIWqe64Nz2alIS8uxUb3SMUp0XK+gBTgQngzBO5V0cQTvd2bAW1sTmssmBOIUskbbdIYeSw0n98VTE7k/B3/zT2ejEXoplkbrxoR1gk3lpfFTVuFajlu4Wid1PTfGRQHiTijobTitzCmmErwl8+uEkc2LplPZK20gJEeTh+mPS9voAL9U8k+fABtUrsTa6Q9AxxcUPWAibycKC4hSQGkdxSiNddUWEUCeYCx0Om0WHs161VPVWdVXaRgcQAZxqz1HJ/pA4TfVQdUvsex/fxSa1uqJO8D6LoOgVRUhX9bxwFgVRwLNJPUR4HLn87CMZwnxTKYba4Qu2h2zCN7E8tbhd5omdHEKzKCaI5WPS1hTJ7sSKhuggOuuBnE8GSEWCzx4Nh9x3QqytK2rjcAQOwTGkglTRbwQ8h1qRak9rwT3/iTUtvsNiP7K6yIYyQ/XAG78BHD3cGxsMtYGur1YBTnFTahfgijd0NhTtuFX83uE/0Wp90qCudEUNLCkpKSkpqYsv2UXJj+qx7fYAAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABSklEQVR4Xu2UvytGURjHv2JQUhRJKWRSMllYDAoLvaEMFossyuAfsNglkywyKFn9BcpiMCo/BmUykIFFfnwe5+o977n34PRmez/1qXuf89yn57nn3CvVgE5s8e7rMpPowkO8wwe8xlGcxQYv71eG8B43s3vrZCKLvX8n/QXr6EKuUDjOOr4GsSjNeCI3mhUNmcKjMBjDXvYtfuCi8p3140gQi9KIx3LFzHPsw3o/KYVpfFO5oPmE88p3moQ9vIrPckV3g7UFHPNiFdiYRazIFdvzYh14hWterALbrSIsbsW2woUYdixixWwcO6yT4UKMGXxUfuv38RK7vVhJbqNsTBs3h42whC94hjty7+gUe8ppX7ThAW6rYIftHA1n1004LjfanAqSoRdvlDD2TyzLdd+Og0r8i4TYV7KBA3LnsCps9FZV8ZnV+Cc+AVm1Nc65qS9oAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJMAAAAaCAYAAACzWm4FAAAE6klEQVR4Xu2aW6hUVRjHv9DI0EpLlCgQozCjNCjtQvhUYEgXSiToJTAUoqfwAvlyeujRF0uEyKwHKyvoQYMwselCGIZFFEUQWERBIFFYVNLl+/Gt1Sy/WXufPdPsPTOc/YM/58xaZ2bW2vu7rn1EWlpaWlrqY1bQTGGOap4frMA5QS0FnKvaLTPrIl2uOuIHK3Ct6iI/WBeXqnaq9qo+UX2b0df//fXowZD2iK3XwwV/TvWM08Ywv1XsfXH8BdV9YW4SuFL6X+92P1AnD6j+UX2sekS1Puhh1fdhbhCPqIv7xYybC+u5WHWPapOYE/whZkDXhflbVYfF9vSN6l7VwjA3KXyhWuIHCyAiHfKDdUGa2Kf6yU8oz4pd9KNiN2kcWKT6TDXlxnM8KmZMtyRjXNy3VE+ozk/GJ4ljYvdmtp/IcLvqoB+sC77sFbHUEeH3KdVXUt0DmqKjekOsGJ0OHAVn+E61VGxfpLZ0r5PIctUpmd6h2PP74WcjbJGzczA3YJvYTbgxGR8XflU97gdLIDKxl8dkvA2JdVUtki9QvSfmWGXd3YOqp2VETQpfSmr4S/JpbxzAMO70gyW8Kfaev8Ui8DiCEb0rVgcuTsaJQEWND43DD6or/ESAFE56W+snAteoXpZuTez1v6GwxZDw/nVurl8oeGMhX0VVC2HWdoMfLCE2FxhT0YUdNStVv4g1OXOTcbqwohvL3G+qVX4iwDXCkXLRjijI5/4p1qScDq8xLF5/2f3TwVgtZkgPSTcs8qV0P+NUqNKBcZRRBfZBOnheurXTMOD7q+qS8J4y9okZO/VrhCMO1ns8GUu5S2xP/PTglO+InS957ha7zz718VlDOULAkEhr1Erpl3jrXqb6XMyTRgGn3f0YE5F2idhFZX9FXh7hrK0K/gyuTK+G95TBNfUpC8PCwDC0HGXGRAR+XXqbFIIC9zNXwgzFmDiroWvjw/yjiamgCAUdG6+SjuqiqjHRVJwIv9NCvyS2x1zYhwVSHAXq5oz0dqhPiq2Xa56D/RUZ04ti6d0Tu8COG49dL1FrYPDaaEh0Op5PVbclr3eJ3ZQq5xtPiX1uVfkwXwS1xXSRkc/BkK5PxvDWsrqJC33SDzYE+087VDq0jnTrQwzqvGQeYj2Va0ZIcZf5QbHzNrpbzqhSKPo5CE2L/77AQ1nMR6qrpZvjrxLb2I/Se45BZ1FU8DUFa855K/Uda6eo5HGKPwLA62mTuZgYlI/COMp+N9YE3HT2xNpiifF2GOuoLpTexyc482uSzxKksjQApMQOj84R+D6i0c/h94HZIb3RwQtLTsktvmkoSrnxKXinX3uaNnLziFQCMcVtDq+bhChKQYwOqQ6INT0YF10WTx+8Y2CAJyV/hsQ9K0rlQGH/gdjzSaL3h6o1Z/1FQ+C5fvFNQ5odtlHH85xRRF3SFUaM4ZMZeFwUme9eRzBAInAuZUcHmQ6+q+zAs1bw3ui5FO2jelZ3h+p3yV/IQUkbixVurk4wICJoUVoqgoh0THojEDVPx42NJXgvm+bcZEpGd/ZEyOckm9w/rDWQNqlBqEWqNAHDIp4l9RtlOXLIdV44GCfjEwGG5AvXUcHZGJ3osCDkNx32N4idYleFEoOzQB+RYKnYGdLAHdlMh2jJQ8+Zws3S23xEbhL7H66WlpaWlpaWlpYx4183fhofHcMJRgAAAABJRU5ErkJggg==>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAAChElEQVR4Xu2XTYiOURTH/xOKxmfUmCwwiUhmISnJakpSkkZplJQFJdkRqRnFQnZiQcpKahazke9pmsZCjbWUUshHFlixsMD/33menvse730+5sUwnl/9a55znufOPeeee+59gZqa/47ZVCc1w9n98z/PGeoN9Z36SH2hjlGzqKXU6uzVSWMh9YB6Rb2ALUxlFNA56iW1n5qX2OdS16l71HNqQWKfTNqp7bD53qJmNrqLWUyNwVZVgXuU0XGY/2/ieKJK3IQFMoj8/bmL+uCNJThJvYathhL3q1gCK+cOZy9EwX6i1nqHQwGPemNJVIIHqLfUKuebKD3UN2o6bKEUeGFp6yUFfAP2YR4bqS3eWJFp1BPqEbUpeZ4oqhzN/TKsyaqKvsKSG2UP7KMd3vEbaYMl7z71DPnbKIZWUs1Kc98KG1OchcXUlPSjh9Qc5/uTaF9rf7+nzjtfjG2wYK8FNgWtZ/maoovFaCL9ncch6nDwrH2o0uwObK2go6+f+uwdEbSSCvhgYFsEm9PywPYTV1EcsM7ju9T6wLYXNrj+SatcgnX/U7DAi0gXSskJ5xQ2sSiq96fIb+26ZWlS4UAXUK7RxVD5raGGqH1ofvbH6KLeUY+RXYI03kVk94TdyLkR6khStvrQ2DXV7U7ALiUhGkg3rg3OXoSakxJ8h1qHrNFUJS1nVVmKVlox6EaoBTqNnPFXIrtFKfgr1AisiRwJ3kupWs5K3FHYeKqUVhmGjRWe5yrz27CV1zbNPZqEsrGM2kn1wlYxdkaqnJXJaAYdurIq62X2ZxkU3HxvhM1HHb/svEqjvZN2xxWhY6qiX1ObYdkcaHRNTVTqCjZW8jU1NTU1rfID7SNsR07f21gAAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAACgElEQVR4Xu2XT0gVURTGPynB0CwpKGlRRhSC4EKiTbQKIsKIKJDaBC0KUtoZuSrQhduoRREIQQS6jMJSQmoR1DqEQLDoDy2qlS5caN/HecPcub439817E6bND37w5tw3991z75k79wEFBf8dLbSdNnpx/3rdM0y/0hX6iy7SQbqF7qWd8VfXjB10in6m87CFyYwSGqWf6CW6rRRvpY/pCzpH20rxvFHl9PrBCjTTU7DxPqNNyeYwu+lr2KoqcR/N6DtYe95o8NfpNzrmtYW4UTITT2GJjCP9+TxLf/rBGjlEH8GSVMK1sAdWzru8eBAl+5t2+Q0eSnjGD2ZkE31LP9AzSJ/gEMfpMt0M60eJB0tbX1LCT2A3pnGEHvODVaIB9dGPsH4aks01MQQb+33YJvuFLiFQMRqEbjrtN+RIP6x0VcIq5TzQSmqz0thPIJ7AEVhOZYluekO3em15425MeSR9Epasu8kpaV2rrSw6WMyU1Oc0rtJrzrUGreew24lVg0pb9+k5rqe0tZJK+IoT2wnru8OJreIhwgnrfTxJe5zYRVjn+pGsKEkl+xLWR9aNK1qoBSTH5G5iFVG9zyJ9a9cp6x6SHd1BdRtdCK2GyvwyApuNw376nb5HfAjSJN5FfE44j5QToV5Jmq0LsNdGhAZwE3YocVFHOnEd9uL1ot9T4iGiclaVRWillYNOhFqg20h5XA4iPkUp+Qf0Ff1BB5zvRdRTznkwDRubu/mpzJ/DVl6PabBaNBv7YIeBc7BVdFfbReWsmaw4g38ZJbfdD8LGoyNw7uPSsxPtjgfcho2K/k0dhc3mrWRTWSZgf+Oq9Z9Dpa5kK5V8QUFBQUG9/AE8X3S/dYzqvQAAAABJRU5ErkJggg==>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAaCAYAAACkVDyJAAABhUlEQVR4Xu2VPyhFcRTHj1DkfxQmBpFSBskii12SQSwWpWRVNkXJqiySTcpgkbDoRRnsMhkogwETg4Xv17ne+73Te9fv3te9pXzqU++e8+ued39/zk/kj9MIK20wSVZhuw1GpVb0Jfaf22dSUsE1+Ag/4Qt8h0uwGnbA3tzQLLEK8oUb8B7OwoYgXg/34Bm8g02wC046HsI553lUCs9EljZ4IfpVLGxphteieVJSwSPRFx1IyCAwAZ9tMCDSlLLYK+yzCQMLZmwwwLtgq2jBfVhhcpYhOGKDAd4Fp0QLjtlERFokfDm+qYLH8BLWmVwi8GBnAvk7jHm4YINx2JHfC/I8nsIBm4gD1/BWdPMUg11mS/I3VQ+8gf1OzBseiTc4DcudeA1cFm0Klk3x29kF6ZZcF2HxbXgOn+CiM+6HK/gBH+CJyXlTBjvhuGhrYoN2v9aFOfbUQZtIihnR9ePZSwWuH28Pzkoq8PoaFr1BVvJTycDutA53RS/kxOFm4tcV21T/pMMX/a5BQzA4lMEAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAaCAYAAACkVDyJAAABaUlEQVR4Xu2VvyvFURTAj1DkV6IwMYiUMkgW+QeUJINYjEpWZTMoWZVFsklZJSx6UQa7TAbKYMDEYOFz3Kd338n36/u+3+6zvE996r1zvu97uu+ee65IhX+gEbuw1sTt98ys4yN+4gu+4wrWYzcOFB7Nhr5wE+9xAVvy8WbcxzO8w1ZswAmcibD3+5cxdOKFuFVpYUsbXovLK5kKHol70aHE7880PttgGrTYKw7ahEEL5mywVDrEFTzAGpOzjOK4DZbKrLiCkzYRgjo8xktsMrkg6MHO5dXPcSzikg2mYVf+Lqjn8RSHbSINuoe34ponCp0y21LcVP14g0NeLDF6JN5wDqu9uB7uVXFDwbIlyTr7V/qkMEW0+A6e4xMue8/9cIUf+IAnJpeYKuzBKXGjSQe0v1ofzelMHbGJUMyL2792mwiF7p/eHvqvlAW9vsbE3SBrxakw6HTawD1xF3JwtJl0dVFNVaE8fAFu+TwLkCnqnwAAAABJRU5ErkJggg==>