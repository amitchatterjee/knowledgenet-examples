### More information to come:

This is an example project for developing a Knowledgenet rules network. This project is in a very early phase.  

**Before you start:**  
The knowledgenet package has not been published to PyPI yet. So, you will have to manually build the package and install it using pip. Please see the instructions in the [knowledgenet project's development documentation](https://github.com/amitchatterjee/knowledgenet/blob/develop/doc/readme-development.md){:target="_blank"}. Once you are done with that, follow the instructions below from a bash shell.

```bash
# Set the PYTHONPATH environment variable
export PYTHONPATH=$HOME/git/knowledgenet-examples/autoins/src

# Change to the PYTHONPATH directory
cd $PYTHONPATH

# Run the rule_runner.py script with specified arguments
python rule_runner.py --rulesPath $HOME/git/knowledgenet-examples/rules --repository 'autoclaims' --factsPath $HOME/git/knowledgenet-examples/data --log debug --outputPath $HOME/git/knowledgenet-examples/target/results --cleanOutput
```


