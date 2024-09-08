```
   _____ _                   ______                   __ 
  / ___/(_)___ _____  ____ _/ / __ )____  ____  _____/ /_
  \__ \/ / __ `/ __ \/ __ `/ / __  / __ \/ __ \/ ___/ __/
 ___/ / / /_/ / / / / /_/ / / /_/ / /_/ / /_/ (__  ) /_  
/____/_/\__, /_/ /_/\__,_/_/_____/\____/\____/____/\__/  
       /____/                                            
```

SignalBoost is a simple, effective feature store for those who want something 
flexible, straight-forward and _cheap_. 

The main components are:

- Registry
  - The registry works as the domain of the feature store. When you've established a set of features, you can register it with the registry and deploy it. 
- Features
  - Features set a framework for generating, saving and interacting with features.  
- Database
  - Database is exactly what it sounds like - interfacing for databases that hold the features.
- Feed
  - Feeds are the input/output pipelines for the features.