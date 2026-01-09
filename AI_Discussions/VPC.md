Building a Virtual Private Cloud (VPC) is like buying a piece of land and building a fenced-in yard with a front gate and a driveway.

Here is the full write-up of the network infrastructure you built.

---

### Phase 1: The Yard (The VPC)

A **VPC** is your own private, isolated section of the AWS cloud.

* **The CIDR Block ():** This defines the size of your network. It provides **65,536** internal IP addresses.
* **The Command:**
```powershell
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=Playground-VPC}]"

```


*In our script, we captured the `VpcId` from the output so the next commands knew where to work.*

### Phase 2: The Room (The Subnet)

A **Subnet** is a slice of your VPC. You can't put a server directly into a VPC; it must live in a subnet.

* **The CIDR Block ():** This smaller range provides **256** IP addresses.
* **Public vs. Private:** Technically, all subnets are private at first. They only become "Public" once you connect them to the Internet Gateway in Step 4.
* **The Command:**
```powershell
aws ec2 create-subnet --vpc-id <VPC-ID> --cidr-block 10.0.1.0/24

```



---

### Phase 3: The Front Gate (Internet Gateway)

An **Internet Gateway (IGW)** is the bridge between your private AWS network and the public internet. Without this, your VPC is a "black hole" with no outside access.

1. **Create it:**
```powershell
aws ec2 create-internet-gateway

```


2. **Attach it:** You must physically "plug" it into your VPC.
```powershell
aws ec2 attach-internet-gateway --vpc-id <VPC-ID> --internet-gateway-id <IGW-ID>

```



### Phase 4: The Driveway (Route Table)

Even with a gate (IGW), your subnet doesn't know it exists. A **Route Table** is a map that tells data packets where to go.

1. **Create the Table:**
```powershell
aws ec2 create-route-table --vpc-id <VPC-ID>

```


2. **Add the "Internet" Route:** We added a rule saying: *"If traffic is looking for any address (), send it to the Internet Gateway."*
```powershell
aws ec2 create-route --route-table-id <RT-ID> --destination-cidr-block 0.0.0.0/0 --gateway-id <IGW-ID>

```


3. **Associate the Subnet:** Finally, we told the subnet to use this map.
```powershell
aws ec2 associate-route-table --subnet-id <SUBNET-ID> --route-table-id <RT-ID>

```



---

### Summary of the Logic

| Component | Real-World Analogy |
| --- | --- |
| **VPC** | The fenced-in yard. |
| **Subnet** | A specific room or shed in the yard. |
| **Internet Gateway** | The front gate to the street. |
| **Route Table** | The GPS/Map telling you that the street is through the front gate. |

### Why This Matters

By scripting this, you've ensured that your lab environment is **repeatable**. If you ever want to start over, you can delete the VPC and run your script again to get the exact same setup in 30 seconds.

**Since we've summarized your security, CLI, and networking, would you like to move on to the final summary of the S3 Static Website deployment we just finished?**