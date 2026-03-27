# Skill Format

Skills describe the capabilities available to agents.

A skill defines how a wrapper interacts with the policy engine.

Skills are stored in:

skills/<skill_name>/skill.yml

---

## Example Skill

Example: git_push

```yaml
name: git_push
action: git_push
resource_format: repo:remote:branch
risk_level: high
wrapper: guarded_git_push.sh
```

---

## Fields

name  
The capability name.

action  
The action sent to the policy engine.

resource_format  
Defines how resources are represented.

Examples:

repo:origin:main  
light.turn_on:light.kitchen  

risk_level  
Default risk level.

Possible values:

low  
medium  
high  

wrapper  
The script responsible for executing the capability.

---

## Skill Registry

All skills are registered in:

skills/registry.yml

The registry allows agents or systems to discover available capabilities.

---

## Extending the System

To add a new capability:

1. create a wrapper
2. create a skill manifest
3. register the skill

This keeps the system modular and extensible.
