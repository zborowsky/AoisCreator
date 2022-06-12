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
    "Drzewa": {
        "Vertices": [
            [
                {
                    "X": 0.0,
                    "Y": 286.398631308811
                },
                {
                    "X": 852.728828058169,
                    "Y": 285.474764756202
                },
                {
                    "X": 928.485885372113,
                    "Y": 468.400342172797
                },
                {
                    "X": 940.496150556031,
                    "Y": 521.060735671514
                },
                {
                    "X": 3.69546621043627,
                    "Y": 655.021385799829
                }
            ]
        ],
        "VideoOccurrences": [
            {
                "AoiState": true,
                "Millage": 10.624071
            },
            {
                "AoiState": false,
                "Millage": 11.316325
            }
        ]
    },
	"Zegar": {
        "Vertices": [
            [
                {
                    "X": 1463.73795761079,
                    "Y": 20.9633911368015
                },
                {
                    "X": 1865.74181117534,
                    "Y": 20.9633911368015
                },
                {
                    "X": 1865.74181117534,
                    "Y": 136.878612716763
                },
                {
                    "X": 1463.73795761079,
                    "Y": 136.878612716763
                }
            ]
        ],
        "VideoOccurrences": [
            {
                "AoiState": true,
                "Millage": 10.375
            }
        ]
    },
    "Budynek": {
        "Vertices": [
            [
                {
                    "X": 742.270055600403,
                    "Y": 449.914285055849
                },
                {
                    "X": 901.189317374928,
                    "Y": 449.914285055849
                },
                {
                    "X": 901.189317374928,
                    "Y": 513.865442297498
                },
                {
                    "X": 742.270055600403,
                    "Y": 513.865442297498
                }
            ],
            [
                {
                    "X": 681.133585625357,
                    "Y": 473.990624381321
                },
                {
                    "X": 872.553002716503,
                    "Y": 473.990624381321
                },
                {
                    "X": 872.553002716503,
                    "Y": 548.482372536469
                },
                {
                    "X": 681.133585625357,
                    "Y": 548.482372536469
                }
            ],
            [
                {
                    "X": 626.339033316393,
                    "Y": 495.569433807453
                },
                {
                    "X": 846.887241475667,
                    "Y": 495.569433807453
                },
                {
                    "X": 846.887241475667,
                    "Y": 579.508357444156
                },
                {
                    "X": 626.339033316393,
                    "Y": 579.508357444156
                }
            ],
            [
                {
                    "X": 520.480911113437,
                    "Y": 487.658168813275
                },
                {
                    "X": 800.998034245393,
                    "Y": 487.658168813275
                },
                {
                    "X": 800.998034245393,
                    "Y": 589.388504269105
                },
                {
                    "X": 520.480911113437,
                    "Y": 589.388504269105
                }
            ],
            [
                {
                    "X": 455.118198941589,
                    "Y": 480.139796268752
                },
                {
                    "X": 771.616693442439,
                    "Y": 480.139796268752
                },
                {
                    "X": 771.616693442439,
                    "Y": 592.544985457262
                },
                {
                    "X": 455.118198941589,
                    "Y": 592.544985457262
                }
            ],
            [
                {
                    "X": 105.320786997435,
                    "Y": 434.217279726261
                },
                {
                    "X": 475.791274593671,
                    "Y": 434.217279726261
                },
                {
                    "X": 475.791274593671,
                    "Y": 562.634730538922
                },
                {
                    "X": 105.320786997435,
                    "Y": 562.634730538922
                }
            ]
        ],
        "VideoOccurrences": [
            {
                "AoiState": true,
                "Millage": 16.12888
            },
            {
                "AoiState": true,
                "Millage": 16.248755
            },
            {
                "AoiState": true,
                "Millage": 16.310875
            },
            {
                "AoiState": true,
                "Millage": 16.382408
            },
            {
                "AoiState": true,
                "Millage": 16.426903
            },
            {
                "AoiState": false,
                "Millage": 16.539181
            }
        ]
    }
}
```

### Different types of aois in Event Configs:
Here we can find 3 different aois, each one of different type.
1. "Drzewa" is static AOI with enable and disable time set. For aois of this type there should be only one entry in Vertices list, and two entries in VideoOccurrences, first one with activation millage second one with deactivation millage.
2. "Zegar" is static AOI with only enable time set. For aois of this type there should be only one entry in Vertices list, and one entry in VideoOccurrences.
3. "Budynek" is dynamic AOI, with enable and disable time. All entries in VideoOccurences should have corresponding entry in Vertices list. In this type of aois there is possibility of having few records with AoiState true in row. 
It's caused by the fact that this aoi can change its shape in time.

## CreateAoisScript requirements
To work correctly this script needs 
* Timestamp from game which will contains following data
  * **Time**
  * **Distance[km]**
  * **offset T**


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
    "SampleVideoName": "Timestamps-2021.10.08-09.54.43 (u01)",
    "Drzewa": [
      {"Status": true, "Time": "00:01:09:42951"},
      {"Status": false, "Time": "00:01:46:244386"}
    ],
    "Zegar": [
      {"Status": true, "Time": "00:00:00:00"}
    ],
    "Budynek": [
      {"Status": true, "Time": "00:06:47:714281"},
      {"Status": true, "Time": "00:06:56:465499"},
      {"Status": true, "Time": "00:07:04:30892"},
      {"Status": true, "Time": "00:07:11:809962"},
      {"Status": true, "Time": "00:07:16:31059"},
      {"Status": false, "Time": "00:07:23:311557"}
    ]
}
```

SampleVideoName - here you need to provide timestamp based on which rest of data will be deduced

Next you provide structure of data in following way:
```
    "AoiName": [
    {"Status": aoiStatus, "Time": timeEntry}
    ]
```
Where 'AoiName' should be replaced with your wishes aoi name, 'aoiStatus' should be replaced with status neither true or false, and "timeEntry" should be replaced with time when status change occurred, be sure that time is formatted in this way hh:mm:ss:ms. 

Be sure that number of records in "VideoOccurences" corresponds to number of provided time records in aois.

For example if you in AoisDurationConfig.json have
```
    "Zamek": [
      {"Status": true, "Time": "00:00:51:795662"},
      {"Status": true, "Time": "00:01:34:228525"},
      {"Status": true, "Time": "00:02:21:342053"},
      {"Status": true, "Time": "00:03:16:073448"},
      {"Status": false, "Time": "00:04:12:989909"}
    ],
```

in EventConfigs.json you must have:
```
    "VideoOccurrences": [
        {
            "AoiState": false,
            "Millage": 0.0
        },
        {
            "AoiState": false,
            "Millage": 0.0
        },
        {
            "AoiState": false,
            "Millage": 0.0
        },
        {
            "AoiState": false,
            "Millage": 0.0
        },
        {
            "AoiState": false,
            "Millage": 0.0
        }
    ]
```
