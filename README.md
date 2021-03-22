# Encrypted Trigger-Action Platform (eTAP)

This repository contains the code and implementation for the paper [Data Privacy in Trigger-Action Systems](https://arxiv.org/pdf/2012.05749.pdf).

eTAP is a privacy-enhancing trigger-action platform  that  executes  trigger-compute-action  rules  without  accessing users’ private data in plaintext. It utilizes a tailored garbled circuit protocol to provide data confidentiality and execution integrity. 


## Get Started

For each party in the trigger-action system, we provide an example Python implementation that follows the eTAP protocols:
- [Trigger-action platform](tap_server): a Flask server that executes the rule uploaded by the client.
- [Trigger service](trigger_server): a Flask server that sends encrypted data to the trigger-action platform.
- [Action service](action_server): a Flask server that decrypts the data received from the trigger-action platform. 
- [Client](client): a Python script that takes a rule description file as input and uploads the information required to execute the rule to the above three servers. 

In addition, we provide a Python module [`etaplib`](etaplib/) that allows developers of trigger and action services to  upgrade their existing Flask API routes to be compatible with eTAP.

Please refer to the `README` in the their own directories for detailed instructions on installation and usage.







## Citation

```
@inproceedings{,
  title = {Data Privacy in Trigger-Action Systems},
  author = {Chen, Yunang and Chowdhury, Amrita Roy and Wang, Ruizhe and Sabelfeld, Andrei and Chatterjee, Rahul and Fernandes, Earlence},
  booktitle = {},
  year = {2021}
}
```

