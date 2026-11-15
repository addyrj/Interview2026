"""Find common AWS waste: unattached EBS volumes, unassociated Elastic IPs, stopped instances.
Usage: python cost_audit.py [region]   (pip install boto3)
Read-only: needs ec2:DescribeVolumes, ec2:DescribeAddresses, ec2:DescribeInstances.
"""
import sys
import boto3


def audit(ec2):
    findings = []
    for page in ec2.get_paginator("describe_volumes").paginate(
        Filters=[{"Name": "status", "Values": ["available"]}]
    ):
        for v in page["Volumes"]:
            findings.append(("unattached-ebs", v["VolumeId"], f"{v['Size']} GiB"))
    for a in ec2.describe_addresses()["Addresses"]:
        if "AssociationId" not in a:
            findings.append(("idle-eip", a.get("AllocationId", a.get("PublicIp")), a["PublicIp"]))
    for page in ec2.get_paginator("describe_instances").paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    ):
        for r in page["Reservations"]:
            for i in r["Instances"]:
                findings.append(("stopped-instance", i["InstanceId"], i["InstanceType"]))
    return findings


if __name__ == "__main__":
    region = sys.argv[1] if len(sys.argv) > 1 else "ap-south-1"
    for kind, rid, detail in audit(boto3.client("ec2", region_name=region)):
        print(f"{kind:18} {rid:24} {detail}")
