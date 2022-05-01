# Pre-requirements
* All required libs installed
* Excel Timestamp
* Event configuration files
* Aois Duration Configuration* (not necessary)

## Required libs:
All required libs placed in requirements.txt

## Excel timestamp Requirement

Every timestamp should be provided in .xlsx format and have the following columns:
* "Time"
* "Distance[km]"
* "event"
* "offset T"

Event columns must always have <strong>"start"</strong> and <strong>"end"</strong> entry

# Script arguments
| Argument        | Description                                         |
|-----------------|-----------------------------------------------------|
| --timestamp_dir | Directory where timestamps files can be found       |
| --config        | Name of aois config data                            |
| --result_dir    | Directory to which, created Aois file will be saved |
 | --data_dir      | Directory where exported eyetracker data are stored |
 | --create_aois   | Select if you want create aois                      |
 | --analyze_data  | Select if you want to analyze Data                  |


# How to create Aois:
At the first run you must run script with argument --update_configuration. 
It will update EventConfigs.json based on AoisDurationConfig.json.

Be sure that every entry of AoisDurationConfig.json have corresponding record in EventConfigs.json

## Commands which you need to execute:
```
main.py --update_configuration --timestamp_dir=Timestamps/timestamp-E2B1-2/
```
To update EventConfigs.json

```
main.py --create_aois --timestamp_dir=Timestamps/timestamp-E2B1-2/
```
To create aois


## How should AoisDurationConfig.json looks like:
```
{
    "SampleVideoName": "Timestamps-2021.10.08-10.06.32 (u01)",
    "FirstAnimalNearTracks": ["00:01:40", "00:01:50"],
}
```

SampleVideoName - here you need to provide timestamp based on which rest of data will be deduced

Next you provide pair AoiName: [Start_time, Stop_time].

## How Should EventConfigs.json looks like:

```
{
    "FirstAnimalNearTracks": {
        "Vertices": [
            {
                "X": 200,
                "Y": 200
            },
            {
                "X": 300,
                "Y": 200
            },
            {
                "X": 300,
                "Y": 100
            },
            {
                "X": 200,
                "Y": 100
            }
        ],
        "VideoOccurrences": [
            0,
            0
        ]
    },
}
```
Be sure that number of records in "VideoOccurences" corresponds to number of provided time records in aois.

For example if you in AoisDurationConfig.json have
```
    "FirstAnimalNearTracks": ["00:01:40", "00:01:50"],
```

in EventConfigs.json you must have:
```
        "VideoOccurrences": [
            0,
            0
        ]
```
