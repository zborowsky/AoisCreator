# What contains this repository:
This repository following scripts:
* **AnalyzeMetricsData** - helps you to analyze oculography data, based on *.Aois file, and exported event based Metrics
* **CreateAoisFiles** - helps you to create multiple *.Aois files based on data provided for one example recording 
* **SplitExportData** - helps you to split one big Metrics export to one files per participant
* **UpdateEventConfigs** - makes changing EventConfigs.json easier

## Required libs:
All required libs placed in requirements.txt

# AnalyzeMetricsData script
This script can analyze metrics data and show you following statistic per Area of Interest Object:

* **Hit rate % of all Whole fixations** 
* **Hit rate % of all Partial fixations**
* **Duration of Whole fixation hit** 
* **Duration of Partial fixation hit** 
* **Duration of all Whole fixations** 
* **Duration of all Partial fixations**

Upon of that you can filter metrics data, based on participant features.
## AnalyzeMetricsData arguments
| Argument              | Description                                                                                 | Default value       |
|-----------------------|---------------------------------------------------------------------------------------------|---------------------|
| **aois_file_dir**     | Directory at which Aois file can be found                                                   | **CreatedAois**     |
| **dump_analyze_data** | Flag which will enable dumping data used in data analysis                                   | **False**           |
| **dump_dir**          | Directory to which analyze data dump will be saved                                          | **AnalyzeDataDump** |
 | **export_data_dir**   | Directory which contains exported metrics data                                              | **ExportedData**    |
 | **filter_data**       | Filter which will be used to filter data syntax is feature/value1,value2;feature2/value1    | **Not set**         |
 | **statistics_data**   | Statistics data which you want to extract from metrics data syntax is feature1/feature2 ... | **Not set**         |


## AnalyzeMetricsData requirements
To work correctly this script needs 
* Event based Metrics exported from Tobii program with default export settings
* Correctly created .Aois file per each of recording (can be created with CreateAoisFiles script)

## How to use AnalyzeMetricsData script
Basic script execution:

```
python AnalyzeMetricsData.py 
```

This execution will only analyze data, without any participant feature included, and without filtration.

*.Aois file will be taken by default from CreatedAois directory if you wish to change it add below argument to basic execution.
```
--aois_file_dir="<directory_which_contains_aois_files>"
```
Tobii metrics will be taken by default from ExportedData directory if you wish to change it add below argument to basic execution.
```
--export_data_dir="<directory_which_contains_exported_metrics>"
```

To save data dumps add following arguments to basic script execution:
```
--dump_analyze_data --dump_dir="<directory_to_which_data_dump_will_be_saved>
```
To add participant feature to report add following argument to basic execution
```
--statistics_data="feature1;feature2"
```
All feature should be separated by ";"

For example if you want to include Age and Gender features to report, argument will look like this:
```
--statistics_data="Age;Gender"
```

To add data filtration add following argument to basic execution
```
--filter_data="feature1/value1;feature2/value1;value2"
```

**Remember that all features which you want to filter must be previously added to statistics data.**

For example if you want filtrate Age equal to 15-23 or 24-29 and Gender Women, argument will look like this:
```
--filter_data="Age/15-23,24-29;Gender/Woman"
```

# CreateAoisScript script
This script can create *.Aois file per all users to which you will provided timestamp and Tobii Metrics.

## CreateAoisScript arguments
| Argument            | Description                                        | Default value         |
|---------------------|----------------------------------------------------|-----------------------|
| **aois_file_dir**   | Directory at which Aois file can be found          | **CreatedAois**       |
| **event_config**    | Path to file which contain Event configs           | **EventConfigs.json** |
| **dump_dir**        | Directory to which analyze data dump will be saved | **AnalyzeDataDump**   |
 | **export_data_dir** | Directory which contains exported metrics data     | **ExportedData**      |
 | **timestamp_dir**   | Path to directory which contains timestamp files   | **Timestamps**        |

## CreateAoisScript requirements
To work correctly this script needs 
* Timestamp from game which will contains following data
  * **Time**
  * **Distance[km]**
  * **offset T**
  * **event** 
    * must always have **"end"** entry, which will be used to calculate approx media duration.

* Event based Metrics exported from Tobii program with default export settings one file per participant, participant id must be placed in filename between **()** for example **(u1)** for participant **u1**
* Properly filled EventConfigs.json (can be done with use of UpdateEventConfigs)

## How to use CreateAoisScript script
Basic script execution:

```
python CreateAoisFiles.py 
```

By default, as event configs, EventConfigs.json will be use, if you wish to change it add below argument to basic execution
```
--event_config="<path_to_new_event_config_json>"
```

*.Aois file will be taken by default from CreatedAois directory if you wish to change it add below argument to basic execution.
```
--aois_file_dir="<directory_which_contains_aois_files>"
```

Tobii metrics will be taken by default from ExportedData directory if you wish to change it add below argument to basic execution.
```
--export_data_dir="<directory_which_contains_exported_metrics>"
```

Timestamp file will be taken by default from Timestamps directory if you wish to change it add below argument to basic execution.
```
--timestamp_dir="<directory_which_contains_timestamps_files>"
```

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
## CreateAoisScript requirements
To work correctly this script needs 
* Timestamp from game which will contains following data
  * **Time**
  * **Distance[km]**
  * **offset T**
  * **event** 
    * must always have **"end"** entry, which will be used to calculate approx media duration.


# SplitExportData script
This script can split one multi participant Tobii Metrics export to export which contain data only per one participant.

## SplitExportData arguments
| Argument            | Description                                       | Default value |
|---------------------|---------------------------------------------------|---------------|
 | **export_data_dir** | Path to metrics data file which you want to split | None          |

## SplitExportData requirements
Tobii event based metrics data, which contains data for more than one participant

## How to use SplitExportData script
Basic script execution:

```
 python SplitExportData.py --export_data_dir="<path_to_tsv_export>"
```


# UpdateEventConfig script
This script can split one multi participant Tobii Metrics export to export which contain data only per one participant.

## UpdateEventConfig arguments
| Argument            | Description                                                             | Default value           |
|---------------------|-------------------------------------------------------------------------|-------------------------|
 | **duration_config** | Config with information about to which timestamp data should be aligned | AoisDurationConfig.json |
 | **event_config**    | Path to file which contain Event configs                                | EventConfigs.json       |
 | **export_data_dir** | Path to metrics data file which you want to split                       | None                    |
 | **timestamp_dir**   | Path to directory which contains timestamp files                        | Timestamps              |

## UpdateEventConfig requirements
* DurationConfigs, details below
* EventConfig details above
* Timestamp from game which will contains following data
  * **Time**
  * **Distance[km]**
  * **offset T**
  * **event** 
    * must always have **"end"** entry, which will be used to calculate approx media duration.
* Tobii event based metrics data, which contains data for more than one participant

## How to use UpdateEventConfig script
Basic script execution:

```
 python UpdateEventConfigs.py
```

By default, as duration configs, AoisDurationConfig.json will be use, if you wish to change it add below argument to basic execution
```
--duration_configs="<path_to_new_duration_config_json>"
```

By default, as event configs, EventConfigs.json will be use, if you wish to change it add below argument to basic execution
```
--event_config="<path_to_new_event_config_json>"
```

Tobii metrics will be taken by default from ExportedData directory if you wish to change it add below argument to basic execution.
```
--export_data_dir="<directory_which_contains_exported_metrics>"
```

Timestamp file will be taken by default from Timestamps directory if you wish to change it add below argument to basic execution.
```
--timestamp_dir="<directory_which_contains_timestamps_files>"
```


## How should AoisDurationConfig.json looks like:
```
{
    "SampleVideoName": "Timestamps-2021.10.08-10.06.32 (u01)",
    "FirstAnimalNearTracks": ["00:01:40", "00:01:50"],
}
```

SampleVideoName - here you need to provide timestamp based on which rest of data will be deduced

Next you provide pair AoiName: [Start_time, Stop_time].

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
