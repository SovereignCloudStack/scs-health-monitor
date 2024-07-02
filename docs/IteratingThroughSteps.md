# How to Iterate several steps in one iteration

## 1. define the steps, that shall be iterated and an additional step that iterates in  
definitions.py:

``` 
@given('I want to test iterations')
def testing(context):
    context.test="•ᴗ•"
    print("Testing iterations")

@then('step one')
def step_one(context):
    print(f"Step one executed {context.test}")

@then('step two')
def step_two(context):
    print(f"Step two executed {context.test}")

@then('step three')
def step_three(context):
    print(f"Step three executed {context.test}")

@then('iterate steps {quantity:d} times')
def step_iterate_steps(context, quantity):
    for i in range(1, quantity + 1):  # Iterate the specified number of times
        print(f"Iteration {i}")
        
        # Invoke the steps programmatically
        context.execute_steps('''
            Then step one
            Then step two
            Then step three
        ''')
``` 

## 2. your feature only calls the step that iterates
```
Feature: i want <quantity> iterations
  Scenario Outline: Example scenario
    Given I want to test iterations
    Then iterate steps <quantity> times
  
    Examples:
    |quantity|
    |3|
```

## 3. and your output looks like this
```
Feature: i want <quantity> iterations # features/iterationtest.feature:1

  Scenario Outline: Example scenario -- @1.1   # features/iterationtest.feature:8
    Given I want to test iterations            # features/steps/definitions.py:602
    Given I want to test iterations            # features/steps/definitions.py:602 0.000s
    Then iterate steps 3 times                 # features/steps/definitions.py:619
Iteration 1
Step one executed •ᴗ•
Step two executed •ᴗ•
Step three executed •ᴗ•
Iteration 2
Step one executed •ᴗ•
Step two executed •ᴗ•
Step three executed •ᴗ•
Iteration 3
Step one executed •ᴗ•
Step two executed •ᴗ•
    Then iterate steps 3 times                 # features/steps/definitions.py:619 0.003s
Feature 'i want <quantity> iterations' passed

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
2 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m0.004s
```