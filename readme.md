### More information to come:

This is an example project for developing a Knowledgenet rules network. This project is in a very early phase.  

**Before you start:**  
The knowledgenet package has not been published to PyPI yet. So, you will have to manually build the package and install it using pip. Please see the instructions in the [knowledgenet project's development documentation](https://github.com/amitchatterjee/knowledgenet/blob/develop/doc/readme-development.md){:target="_blank"}. Once you are done with that, follow the instructions below from a shell.

```bash
# Change as needed
export KNOWLEDGENET_EX_HOME=$HOME/git/knowledgenet-examples/

# One-time setup
cd $KNOWLEDGENET_EX_HOME
pip install -r requirements.txt

# Set the PYTHONPATH environment variable
export PYTHONPATH=$KNOWLEDGENET_EX_HOME/autoins/src

# Change to the root of the auto insurance example directory 
cd $KNOWLEDGENET_EX_HOME/autoins

# Run the rule_runner.py script with specified arguments
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log debug --outputPath $KNOWLEDGENET_EX_HOME/target/results --cleanOutput

# Run the rule_runner.py script with tracing
python src/rule_runner.py --rulesPath $KNOWLEDGENET_EX_HOME/autoins/rules --factsPaths $KNOWLEDGENET_EX_HOME/autoins/data --log info --outputPath $KNOWLEDGENET_EX_HOME/target/results --cleanOutput --trace $KNOWLEDGENET_EX_HOME/target/trace.json

# Run pytest
python -m pytest -rPX
```
