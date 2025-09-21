# Economic-security-risk-sim
“Monte Carlo simulation of activist-driven technology leakage risks and downgrade probability”
This repository provides a **Monte Carlo simulation model** to analyze
how **foreign activist investors** and potential **technology leakage**
(e.g., through indirect accounting information inference) could affect:

- Firm-level **competitiveness**
- **Cash flow and leverage** trajectories
- **Credit rating downgrade probabilities**

The model is designed for academic and policy research on
**economic security** and **financial stability**.

---

## ✨ Key Features
- **Monte Carlo engine** simulating revenue, margins, and debt service capacity  
- **Leakage scenario toggle**:
  - Probability of event (`P_LEAK`)
  - Severity of impact on growth and margins (`SEVERITY`)
  - Detection lag and mitigation strength
- **Credit rating downgrade trigger**:
  - Interest coverage (EBITDA / Interest)
  - Leverage (Debt / EBITDA)
  - Consecutive-year breach rules
- **Sensitivity analysis**:
  - Downgrade probability vs leakage severity
- **Visualization**:
  - Probability curves
  - Example paths
  - Distribution of downgrade timing

---

## 🛠 Installation
```bash
git clone https://github.com/<YourUserName>/economic-security-risk-sim.git
cd economic-security-risk-sim
pip install -r requirements.txt
Dependencies:

numpy

pandas

matplotlib

🚀 Usage
Run the simulation with default parameters:

bash
python risk_simulation.py
Outputs:

Console summary of downgrade probabilities

risk_simulation_summary.csv with scenario sweep results

Plots (downgrade probability vs severity, example paths, downgrade timing)

📊 Example Output
Downgrade probability vs leakage severity


📚 Academic / Policy Context
This tool is intended for:

Academic conferences on economics, finance, and security studies

Policy think tanks analyzing FEFTA, CFIUS, NSI Act, and equivalent regimes

Industry case studies (semiconductors, EV batteries, critical infrastructure)

Scenario planning for economic security legislation

It operationalizes the link between:

Technology protection

Corporate governance / activist investors

Credit market stability

📄 License
This project is licensed under the MIT License.

✍️ Citation
If you use this model in academic work, please cite as:

Hideki. Economic Security Risk Simulation: Monte Carlo Analysis of Activist-driven Technology Leakage and Downgrade Probability. GitHub (2025).

🤝 Contributions
Contributions, forks, and policy-oriented extensions are welcome.
Please open an Issue or Pull Request if you would like to collaborate.



