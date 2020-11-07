# Example Rules

## IFTTT Example Rules

* 01: x0 contain `#twitter`
* 02: x1 contain `lostphone`
* 03: x4 eq `test_user@sample_website.com`
* 04: x0 contain `#facebook`
* 05: x0 contain `To-do`
* 06: x0 contain `Evernote`
* 07: x0 contain `birthday`
* 08: x0 contain `#facebook`
* 09: x0 contain `#slack`
* 10: x0 contain `ToDo`

## Zapier Example Rules


#### Contains

| Rule ID | Trigger Word |
| ------- | ------------ |
| 1 | sale |
| 6 | name |
| 8 | invalid_disposable_unknown |
| 9 | content |
| 16 | Zapier |
| 18 | MP4 AVI WMA MOV |
| 20 | Supplier |
| 25 | confirm |
| 26 | Veryimportant |
| 27 | finance |
| 30 | ticket |
| 45 | sold rented |
| 46 | Available |
| 47 | Bid |
| 48 | target | 
| 50 | target |


#### Equal

| Rule ID | Trigger Word |
| ------- | ------------ |
| 2 | No Active Alerts |
| 3 | Closed Won |
| 4 | TripAdvisor| 
| 11 | .pdf |
| 21 | False |
| 23 | Seller |
| 31 | 50-closed |
| 33 | \from_input |
| 36 | Meeting | 
| 42 | True |
| 43 | succeeded |
| 49 | won |
| 51 | True |

#### Split

| Rule ID | Trigger Word |
| ------- | ------------ |
| 5 | . |
| 12 | \space |
| 13 | \space |
| 14 | \space |
| 15 | \space |

`TODO`: Generate DFA

#### Lookup

| Rule ID | Trigger Word |
| ------- | ------------ |
| 6 | [See file for detail] |
| 23 | USA -> test |
| 40 | source -> traget |
| 44 | \space -> target |

#### Digital 

| Rule ID | Trigger Word |
| ------- | ------------ |
| 19 | > |
| 24 | / |
| 28 | > |
| 29 | * |

#### Exists (Use eq)

| Rule ID |
| ------- |
| 7 |
| 10 |
| 17 |
| 22 |
| 32 |
| 33 |
| 35 |
| 37 |
| 38 |
| 39 |

#### Others

| Rule ID | Rule Name | Trigger Word |
| ------- | --------- | ------------ |
| 40 | start_with | $request |

`NOTE`: bool operations are omitted in this table